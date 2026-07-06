from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import dgl
    DGL_AVAILABLE = True
except ImportError:
    DGL_AVAILABLE = False

from src.features import (
    compute_all_features,
    compute_rdkit_descriptors,
    canonicalize_smiles,
    is_valid_smiles,
    get_feature_names,
    feature_dimension,
)
from src.feature_importance import get_model_feature_importance
from src.models import load_model
from src.config import MODELS_DIR, logger, MAX_BATCH_SIZE
from src.endpoints import ENDPOINTS, LEGACY_KEYS

HYBRID_MODEL_PATH = MODELS_DIR / "hybrid_model.pt"


class ADMETPredictor:
    def __init__(self):
        self._models: dict[str, object] = {}
        self._model_paths: dict[str, Path] = {}
        self._hybrid_model = None
        self._hybrid_device = None
        self._scan_model_files()
        self._try_load_hybrid()
        self._expected_dim = feature_dimension() if self._model_paths else None
        logger.info("Found %d model files, expected feature dim: %s", len(self._model_paths), self._expected_dim)

    def _scan_model_files(self):
        model_keys = list(LEGACY_KEYS)
        herg_prefer = MODELS_DIR / "herg_model_expanded.pkl"
        herg_fallback = MODELS_DIR / "herg_model.pkl"

        for key in model_keys:
            if key == "herg":
                path = herg_prefer if herg_prefer.exists() else herg_fallback
            else:
                path = MODELS_DIR / f"{key}_model.pkl"
            if path.exists():
                self._model_paths[key] = path
            else:
                logger.warning("Model %s not found at %s", key, path)

    def _try_load_hybrid(self):
        if not HYBRID_MODEL_PATH.exists():
            logger.info("No hybrid model found at %s, using LightGBM only", HYBRID_MODEL_PATH)
            return
        try:
            if not DGL_AVAILABLE or not TORCH_AVAILABLE:
                logger.warning("DGL or torch not installed, cannot load hybrid model")
                return
            import torch
            from src.hybrid_model import HybridMultiTask
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            checkpoint = torch.load(HYBRID_MODEL_PATH, map_location=device, weights_only=True)
            model = HybridMultiTask(
                desc_dim=checkpoint["desc_dim"],
                task_names=checkpoint["task_keys"],
                task_types=checkpoint["task_types"],
                node_feat_dim=checkpoint["node_feat_dim"],
                edge_feat_dim=checkpoint["edge_feat_dim"],
            ).to(device)
            model.load_state_dict(checkpoint["model_state_dict"])
            model.eval()
            self._hybrid_model = model
            self._hybrid_device = device
            logger.info("Hybrid model loaded on %s", device)
        except Exception as e:
            logger.warning("Failed to load hybrid model: %s", e)

    @property
    def hybrid_available(self) -> bool:
        return self._hybrid_model is not None

    def _get_model(self, key: str):
        if key not in self._models:
            path = self._model_paths.get(key)
            if path is None:
                raise ValueError(f"Model '{key}' not available")
            self._models[key] = load_model(path)
            logger.debug("Lazy-loaded model: %s", path)
        return self._models[key]

    @property
    def is_ready(self) -> bool:
        return len(self._model_paths) >= 5 or self.hybrid_available

    @property
    def models(self) -> dict:
        return dict(self._model_paths)

    @property
    def model_keys(self) -> list[str]:
        return list(self._model_paths.keys())

    @property
    def feature_importances(self) -> dict:
        result = {}
        for key in self._model_paths:
            imp = get_model_feature_importance(key)
            if imp:
                result[key] = imp
        return result

    def _validate_feature(self, feat: np.ndarray) -> np.ndarray:
        if self._expected_dim is not None and feat.shape[-1] != self._expected_dim:
            logger.warning(
                "Feature dim mismatch: got %d, expected %d",
                feat.shape[-1], self._expected_dim,
            )
        return feat

    @staticmethod
    def _extract_descriptors(feat: np.ndarray) -> dict:
        from src.features import get_descriptor_names
        desc_names = get_descriptor_names()
        n_desc = len(desc_names)
        return dict(zip(desc_names, feat[:n_desc].tolist()))

    def _predict_hybrid(self, smiles: str, canon: str) -> dict:
        import torch
        from src.gnn_features import mol_to_graph
        feat = compute_all_features(canon)
        if feat is None:
            return {"error": f"Could not compute features for: {smiles}"}
        desc_tensor = torch.tensor(feat, dtype=torch.float32, device=self._hybrid_device).unsqueeze(0)
        g = mol_to_graph(canon)
        if g is None:
            return None
        g = g.to(self._hybrid_device)
        h = g.ndata["h"]
        e = g.edata.get("e")
        with torch.no_grad():
            if hasattr(self._hybrid_model, 'task_names'):
                outputs = self._hybrid_model(g, h, e, desc_tensor)
            else:
                outputs = {"default": self._hybrid_model(g, h, e, desc_tensor)}
        results = {"SMILES": canon}
        if hasattr(self._hybrid_model, 'task_names'):
            for task_key in self._hybrid_model.task_names:
                cfg = ENDPOINTS.get(task_key)
                if cfg is None:
                    continue
                label = cfg["name"]
                raw = outputs[task_key].squeeze(-1).item()
                if cfg["task"] == "classification":
                    prob = float(torch.sigmoid(torch.tensor(raw)))
                    results[label] = round(prob, 3)
                    classify_fn = cfg.get("classify")
                    if classify_fn:
                        extra = classify_fn(prob)
                        if extra:
                            results.update(extra)
                else:
                    results[label] = round(raw, 3)
                    classify_fn = cfg.get("classify")
                    if classify_fn:
                        extra = classify_fn(raw)
                        if extra:
                            results.update(extra)
        desc = self._extract_descriptors(feat)
        results.update(desc)
        return results

    def predict_single(self, smiles: str) -> dict:
        if not self.is_ready:
            return {"error": "Models not loaded. Train models first."}
        if not smiles or not smiles.strip():
            return {"error": "Empty SMILES string"}
        canon = canonicalize_smiles(smiles)
        if canon is None:
            return {"error": f"Invalid SMILES: {smiles}"}

        if self.hybrid_available:
            try:
                result = self._predict_hybrid(smiles, canon)
                if result is not None:
                    return result
            except Exception as e:
                logger.warning("Hybrid prediction failed, falling back to LightGBM: %s", e)

        feat = compute_all_features(canon)
        if feat is None:
            return {"error": f"Could not compute features for: {smiles}"}
        feat_2d = self._validate_feature(feat.reshape(1, -1))
        results = {"SMILES": canon}

        for key in self._model_paths:
            cfg = ENDPOINTS.get(key)
            if cfg is None:
                continue
            model = self._get_model(key)
            if cfg["task"] == "classification":
                prob = float(model.predict_proba(feat_2d)[0, 1])
                results[cfg["name"]] = round(prob, 3)
                classify_fn = cfg.get("classify")
                if classify_fn:
                    extra = classify_fn(prob)
                    if extra:
                        results.update(extra)
            else:
                val = float(model.predict(feat_2d)[0])
                results[cfg["name"]] = round(val, 3) if key != "ppbr" else round(val, 1)
                classify_fn = cfg.get("classify")
                if classify_fn:
                    extra = classify_fn(val)
                    if extra:
                        results.update(extra)

        desc = self._extract_descriptors(feat)
        results.update(desc)
        return results

    def predict_batch(self, smiles_list: list[str]) -> list[dict]:
        if not smiles_list:
            return []
        smiles_list = [s.strip() for s in smiles_list if s and s.strip()]
        if len(smiles_list) > MAX_BATCH_SIZE:
            logger.warning(
                "Batch size %d exceeds limit %d, truncating",
                len(smiles_list), MAX_BATCH_SIZE,
            )
            smiles_list = smiles_list[:MAX_BATCH_SIZE]

        canon_list: list[str] = []
        valid_indices: list[int] = []
        for i, smi in enumerate(smiles_list):
            canon = canonicalize_smiles(smi)
            if canon is not None:
                canon_list.append(canon)
                valid_indices.append(i)

        if not canon_list:
            return [{"error": "No valid SMILES"}] if len(smiles_list) == 0 else [{"error": f"Invalid SMILES: {s}"} for s in smiles_list]

        feat_list: list[np.ndarray | None] = [None] * len(canon_list)
        with ThreadPoolExecutor(max_workers=8) as pool:
            fut_map = {pool.submit(compute_all_features, c): i for i, c in enumerate(canon_list)}
            for fut in as_completed(fut_map):
                idx = fut_map[fut]
                try:
                    feat_list[idx] = fut.result()
                except Exception:
                    feat_list[idx] = None
        valid_feat = [(i, c, f) for i, (c, f) in enumerate(zip(canon_list, feat_list)) if f is not None]
        if not valid_feat:
            return [{"error": "Could not compute features"} for _ in smiles_list]

        indices = [vf[0] for vf in valid_feat]
        canons = [vf[1] for vf in valid_feat]
        feats = np.array([vf[2] for vf in valid_feat], dtype=np.float32)

        all_results: list[dict | None] = [None] * len(smiles_list)
        for idx, canon, feat_vec in zip(indices, canons, feats):
            all_results[valid_indices[idx]] = {"SMILES": canon}

        for key in self._model_paths:
            cfg = ENDPOINTS.get(key)
            if cfg is None:
                continue
            model = self._get_model(key)
            batch_feats = self._validate_feature(feats)
            if cfg["task"] == "classification":
                probs = model.predict_proba(batch_feats)[:, 1]
                classify_fn = cfg.get("classify")
                for j, idx in enumerate(indices):
                    prob = float(probs[j])
                    orig_idx = valid_indices[idx]
                    all_results[orig_idx][cfg["name"]] = round(prob, 3)
                    if classify_fn:
                        extra = classify_fn(prob)
                        if extra:
                            all_results[orig_idx].update(extra)
            else:
                vals = model.predict(batch_feats)
                classify_fn = cfg.get("classify")
                for j, idx in enumerate(indices):
                    val = float(vals[j])
                    orig_idx = valid_indices[idx]
                    all_results[orig_idx][cfg["name"]] = round(val, 3) if key != "ppbr" else round(val, 1)
                    if classify_fn:
                        extra = classify_fn(val)
                        if extra:
                            all_results[orig_idx].update(extra)

        for idx, canon, feat_vec in zip(indices, canons, feats):
            orig_idx = valid_indices[idx]
            desc = self._extract_descriptors(feat_vec)
            all_results[orig_idx].update(desc)

        return [r if r is not None else {"error": "Prediction failed"} for r in all_results]

    def predict_dataframe(
        self, smiles_list: list[str], drug_names: list[str] | None = None,
    ) -> pd.DataFrame:
        results = self.predict_batch(smiles_list)
        df = pd.DataFrame(results)
        if drug_names:
            df.insert(0, "Drug", drug_names)
        else:
            df.insert(
                0, "Drug",
                [f"Molecule_{i}" for i in range(len(smiles_list))],
            )
        return df

    def predict_validated(self, smiles_dict: dict[str, str]) -> pd.DataFrame:
        results = []
        for name, smi in smiles_dict.items():
            r = self.predict_single(smi)
            if "error" not in r:
                r["Drug"] = name
                results.append(r)
        return pd.DataFrame(results)


def create_predictor() -> ADMETPredictor:
    return ADMETPredictor()
