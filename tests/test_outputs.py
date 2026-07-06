import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

from src.config import MODELS_DIR, DATA_DIR


def test_training_results_exist():
    path = MODELS_DIR / "training_results.json"
    assert path.exists(), "training_results.json not found. Run python run_train.py"
    with open(path) as f:
        data = json.load(f)
    expected = {"solubility", "caco2", "herg", "lipophilicity", "pgp"}
    assert expected.issubset(data.keys()), f"Missing models: {expected - data.keys()}"


def test_all_model_files_exist():
    for key in ["solubility", "caco2", "herg", "lipophilicity", "pgp"]:
        path = MODELS_DIR / f"{key}_model.pkl"
        assert path.exists(), f"Model file not found: {path}"


def test_datasets_info_exist():
    path = DATA_DIR / "datasets_info.json"
    assert path.exists()
    with open(path) as f:
        data = json.load(f)
    expected = {"solubility", "caco2", "herg", "lipophilicity", "pgp"}
    assert expected.issubset(data.keys())


def test_lipophilicity_metric():
    path = MODELS_DIR / "training_results.json"
    with open(path) as f:
        data = json.load(f)
    lipo = data.get("lipophilicity", {})
    assert lipo.get("test_r2", 0) > 0.5, f"Lipophilicity R² too low: {lipo.get('test_r2')}"


def test_pgp_metric():
    path = MODELS_DIR / "training_results.json"
    with open(path) as f:
        data = json.load(f)
    pgp = data.get("pgp", {})
    assert pgp.get("test_auc", 0) > 0.8, f"P-gp AUC too low: {pgp.get('test_auc')}"
