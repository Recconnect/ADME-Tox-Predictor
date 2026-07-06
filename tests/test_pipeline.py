import json
import time
import pytest
from pathlib import Path
from src.predict import ADMETPredictor
from src.features import canonicalize_smiles, is_valid_smiles
from src.radar import compute_scores, plot_radar
from src.pdf_report import generate_pdf

VALID_SMILES = [
    ("CCO", True),
    ("CC(=O)Oc1ccccc1C(=O)O", True),
    ("invalid_smiles_xxx", False),
    ("", False),
]

VALIDATION_DRUGS = [
    ("Aspirin", "CC(=O)Oc1ccccc1C(=O)O"),
    ("Ibuprofen", "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O"),
    ("Paracetamol", "CC(=O)Nc1ccc(O)cc1"),
    ("Caffeine", "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"),
    ("Metformin", "CN(C)C(=N)N=C(N)N"),
]


def test_smiles_validation():
    for smi, expected in VALID_SMILES:
        assert is_valid_smiles(smi) == expected


def test_smiles_canonicalization():
    inputs = ["CCO", "C(C)O", "OCC"]
    canonical = canonicalize_smiles(inputs[0])
    for smi in inputs:
        assert canonicalize_smiles(smi) == canonical


def test_smiles_to_prediction_json():
    predictor = ADMETPredictor()
    result = predictor.predict_single("CCO")
    json_str = json.dumps(result, ensure_ascii=False, default=str)
    parsed = json.loads(json_str)
    assert "Solubility (logS)" in parsed
    assert "Caco-2 Class" in parsed or "Caco-2 Permeability" in parsed


def test_batch_prediction():
    predictor = ADMETPredictor()
    smiles_list = [smi for _, smi in VALIDATION_DRUGS]
    results = predictor.predict_batch(smiles_list)
    assert len(results) == len(smiles_list)
    for r in results:
        assert "Solubility (logS)" in r


def test_radar_scores_compute():
    predictor = ADMETPredictor()
    result = predictor.predict_single("CCO")
    scores = compute_scores(result)
    assert len(scores) == 10
    for s in scores:
        assert 0.0 <= s <= 1.0


def test_radar_plot_generates():
    import matplotlib
    matplotlib.use("Agg")
    predictor = ADMETPredictor()
    result = predictor.predict_single("CCO")
    scores = compute_scores(result)
    fig = plot_radar(scores, lang="ru")
    assert fig is not None


def test_pdf_report_generates(tmp_path):
    import matplotlib
    matplotlib.use("Agg")
    predictor = ADMETPredictor()
    result = predictor.predict_single("CCO")
    scores_list = [0.5] * 10
    pdf_path = tmp_path / "test_report.pdf"
    pdf_data = generate_pdf("CCO", result, scores_list, lang="ru")
    with open(pdf_path, "wb") as f:
        f.write(pdf_data)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1000


def test_pipeline_100_drugs_time():
    predictor = ADMETPredictor()
    smiles_list = [smi for _, smi in VALIDATION_DRUGS] * 20
    start = time.perf_counter()
    results = predictor.predict_batch(smiles_list)
    elapsed = time.perf_counter() - start
    assert len(results) == len(smiles_list)
    assert elapsed < 30.0, f"Batch 100 took {elapsed:.1f}s, expected <30s"
