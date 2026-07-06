import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.features import canonicalize_smiles, compute_all_features, feature_dimension
from src.models import save_model, load_model
from src.config import MODELS_DIR, VALIDATION_DRUGS


class TestPredictor:
    @pytest.fixture
    def predictor(self):
        from src.predict import ADMETPredictor

        return ADMETPredictor()

    def test_predictor_loaded(self, predictor):
        assert predictor.is_ready
        assert len(predictor.models) >= 3

    def test_predict_ethanol(self, predictor):
        result = predictor.predict_single("CCO")
        assert "error" not in result, result.get("error")
        assert "Solubility (logS)" in result
        assert "Caco-2 Class" in result
        assert "hERG Class" in result
        assert "Lipophilicity (logD)" in result
        assert "P-gp Class" in result

    def test_predict_aspirin(self, predictor):
        result = predictor.predict_single("CC(=O)Oc1ccccc1C(=O)O")
        assert "error" not in result, result.get("error")
        assert isinstance(result.get("Solubility (logS)"), (int, float))

    def test_predict_caffeine(self, predictor):
        result = predictor.predict_single("CN1C=NC2=C1C(=O)N(C(=O)N2C)C")
        assert "error" not in result, result.get("error")
        assert result.get("SolubilityClass") in (
            "Soluble", "Poorly soluble"
        )

    def test_invalid_smiles(self, predictor):
        result = predictor.predict_single("INVALID_SMILES")
        assert "error" in result

    def test_empty_smiles(self, predictor):
        result = predictor.predict_single("")
        assert "error" in result

    def test_predict_batch(self, predictor):
        smiles = ["CCO", "CC(=O)Oc1ccccc1C(=O)O", "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"]
        results = predictor.predict_batch(smiles)
        assert len(results) == 3
        for r in results:
            assert "error" not in r

    def test_predict_dataframe(self, predictor):
        smiles = ["CCO", "CCCO"]
        df = predictor.predict_dataframe(
            smiles, drug_names=["Ethanol", "Propanol"]
        )
        assert len(df) == 2
        assert "Drug" in df.columns
        assert list(df["Drug"]) == ["Ethanol", "Propanol"]

    def test_predict_validated(self, predictor):
        df = predictor.predict_validated(VALIDATION_DRUGS)
        assert len(df) == len(VALIDATION_DRUGS)
        assert "Drug" in df.columns
        assert "Solubility (logS)" in df.columns
        assert all(
            name in df["Drug"].values for name in VALIDATION_DRUGS
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
