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


class ADMETPredictor:
    def __init__(self):
        self.models = {}
        self._feature_names = None
        self._expected_dim = None
        self._load_models()

    def _load_models(self):
        for key in ["solubility", "caco2", "herg"]:
            path = MODELS_DIR / f"{key}_model.pkl"
            if path.exists():
                self.models[key] = load_model(path)
                logger.info("Loaded model: %s", path)
            else:
                logger.warning("Model %s not found at %s", key, path)

        if self.models:
            self._expected_dim = feature_dimension()
            logger.info("Expected feature dimension: %d", self._expected_dim)

    @property
    def is_ready(self) -> bool:
        return len(self.models) >= 3

    @property
    def feature_importances(self) -> dict:
        result = {}
        for key in self.models:
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

        if "solubility" in self.models:
            logS = float(self.models["solubility"].predict(feat_2d)[0])
            results["Solubility (logS)"] = round(logS, 3)
            results["SolubilityClass"] = "Soluble" if logS > -4 else "Poorly soluble"

        if "caco2" in self.models:
            prob = float(self.models["caco2"].predict_proba(feat_2d)[0, 1])
            results["Caco-2 Permeability"] = round(prob, 3)
            results["Caco-2 Class"] = "High permeability" if prob > 0.5 else "Low permeability"

        if "herg" in self.models:
            prob = float(self.models["herg"].predict_proba(feat_2d)[0, 1])
            results["hERG Toxicity Risk"] = round(prob, 3)
            results["hERG Class"] = "Toxic (high risk)" if prob > 0.5 else "Safe (low risk)"

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
