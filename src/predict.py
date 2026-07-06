from pathlib import Path

import numpy as np
import pandas as pd

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


_REGRESSION_CONFIGS = [
    ("solubility", "Solubility (logS)", lambda v: {"SolubilityClass": "Soluble" if v > -4 else "Poorly soluble"}),
    ("lipophilicity", "Lipophilicity (logD)", lambda v: None),
    ("ppbr", "PPB (plasma binding)", lambda v: {"PPB Class": "Highly bound (>90%)" if v > 90 else "Moderately bound (50-90%)" if v > 50 else "Weakly bound (<50%)"}),
]

_CLASSIFICATION_CONFIGS = [
    ("caco2", "Caco-2 Permeability", lambda v: {"Caco-2 Class": "High permeability" if v > 0.5 else "Low permeability"}),
    ("herg", "hERG Toxicity Risk", lambda v: {"hERG Class": "Toxic (high risk)" if v > 0.5 else "Safe (low risk)"}),
    ("pgp", "P-gp Inhibition", lambda v: {"P-gp Class": "Inhibitor (high risk)" if v > 0.5 else "Non-inhibitor (low risk)"}),
    ("cyp3a4", "CYP3A4 Inhibition", lambda v: {"CYP3A4 Class": "Inhibitor" if v > 0.5 else "Non-inhibitor"}),
    ("cyp2d6", "CYP2D6 Inhibition", lambda v: {"CYP2D6 Class": "Inhibitor" if v > 0.5 else "Non-inhibitor"}),
    ("ames", "Ames Mutagenicity", lambda v: {"Ames Class": "Mutagenic (positive)" if v > 0.5 else "Non-mutagenic (negative)"}),
    ("bioavailability", "Bioavailability", lambda v: {"Bioavailability Class": "High" if v > 0.5 else "Low"}),
]


class ADMETPredictor:
    def __init__(self):
        self._models: dict[str, object] = {}
        self._model_paths: dict[str, Path] = {}
        self._scan_model_files()
        self._expected_dim = feature_dimension() if self._model_paths else None
        logger.info("Found %d model files, expected feature dim: %s", len(self._model_paths), self._expected_dim)

    def _scan_model_files(self):
        model_keys = [
            "solubility", "caco2", "herg", "lipophilicity", "pgp",
            "cyp3a4", "cyp2d6", "ames", "bioavailability", "ppbr",
        ]
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
        return len(self._model_paths) >= 5

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

    def predict_single(self, smiles: str) -> dict:
        if not self.is_ready:
            return {"error": "Models not loaded. Train models first."}
        if not smiles or not smiles.strip():
            return {"error": "Empty SMILES string"}
        canon = canonicalize_smiles(smiles)
        if canon is None:
            return {"error": f"Invalid SMILES: {smiles}"}
        feat = compute_all_features(canon)
        if feat is None:
            return {"error": f"Could not compute features for: {smiles}"}
        feat_2d = self._validate_feature(feat.reshape(1, -1))
        results = {"SMILES": canon}

        for key, label, class_fn in _CLASSIFICATION_CONFIGS:
            if key in self._model_paths:
                model = self._get_model(key)
                prob = float(model.predict_proba(feat_2d)[0, 1])
                results[label] = round(prob, 3)
                extra = class_fn(prob)
                if extra:
                    results.update(extra)

        for key, label, extra_fn in _REGRESSION_CONFIGS:
            if key in self._model_paths:
                model = self._get_model(key)
                val = float(model.predict(feat_2d)[0])
                results[label] = round(val, 3) if key != "ppbr" else round(val, 1)
                extra = extra_fn(val)
                if extra:
                    results.update(extra)

        desc = compute_rdkit_descriptors(canon)
        if desc:
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
        return [self.predict_single(smi) for smi in smiles_list]

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
