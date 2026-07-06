import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
    assert data["models_loaded"] >= 3


def test_predict_valid():
    resp = client.post("/predict", json={"smiles": "CCO"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["canonical_smiles"] == "CCO"
    assert len(data["properties"]) > 0
    assert data["error"] is None


def test_predict_invalid():
    resp = client.post("/predict", json={"smiles": "INVALID"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"] is not None


def test_predict_empty():
    resp = client.post("/predict", json={"smiles": ""})
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"] is not None


def test_batch():
    resp = client.post("/batch", json={"smiles": ["CCO", "CC(=O)Oc1ccccc1C(=O)O", ""]})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert data["failed"] == 1


def test_validate():
    resp = client.get("/validate")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 10
