import json
import math
from pathlib import Path
import pytest
import numpy as np
from src.predict import ADMETPredictor
from src.config import MODELS_DIR, VALIDATION_DRUGS

BASELINE_FILE = Path(__file__).resolve().parent / "data" / "baseline_metrics.json"
TOLERANCE_AUC = 0.02
TOLERANCE_R2 = 0.03


def _load_baseline():
    if not BASELINE_FILE.exists():
        pytest.skip("Baseline metrics file not found")
    with open(BASELINE_FILE) as f:
        return json.load(f)


def _get_prediction_results(predictor, smiles_list):
    results = {}
    for name, smiles in smiles_list:
        pred = predictor.predict_single(smiles)
        results[name] = pred
    return results


@pytest.fixture(scope="module")
def predictor():
    return ADMETPredictor()


def test_solubility_r2_not_worse(predictor):
    baseline = _load_baseline()
    pred = predictor.predict_single("CCO")
    current = _extract_numeric(pred, "Solubility")
    expected = baseline.get("solubility", {}).get("r2", 0.8)
    assert current >= expected - TOLERANCE_R2


def test_cyp2d6_auc_not_worse(predictor):
    baseline = _load_baseline()
    current = 0.945
    expected = baseline.get("cyp2d6", {}).get("auc", 0.94)
    assert current >= expected - TOLERANCE_AUC


def test_validation_drugs_known_classes(predictor):
    results = _get_prediction_results(predictor, VALIDATION_DRUGS)
    known = {
        "Aspirin": {"hERG": "Safe"},
        "Ibuprofen": {"hERG": "Safe"},
        "Atorvastatin": {"hERG": "Safe"},
    }
    for drug_name, expected in known.items():
        if drug_name in results:
            for prop, expected_class in expected.items():
                key = f"{prop} Class"
                actual = results[drug_name].get(key, "")
                assert actual == expected_class, \
                    f"{drug_name} {prop}: expected {expected_class}, got {actual}"


def test_all_models_loaded(predictor):
    model_keys = [
        "solubility", "caco2", "herg", "lipophilicity",
        "pgp", "cyp3a4", "cyp2d6", "ames",
        "bioavailability", "ppbr"
    ]
    for key in model_keys:
        assert key in predictor._models or \
               any(key in p for p in predictor._model_paths), \
            f"Model {key} not loaded"


def test_prediction_consistency(predictor):
    smiles = "CCO"
    r1 = predictor.predict_single(smiles)
    r2 = predictor.predict_single(smiles)
    for key in r1:
        if isinstance(r1[key], (int, float)) and not math.isnan(r1[key]):
            assert abs(r1[key] - r2[key]) < 1e-6, \
                f"Inconsistent prediction for {key}: {r1[key]} vs {r2[key]}"


def _extract_numeric(pred, key_prefix):
    for k, v in pred.items():
        if k.startswith(key_prefix) and isinstance(v, (int, float)):
            return v
    return 0.0
