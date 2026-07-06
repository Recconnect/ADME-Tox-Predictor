import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

from src.config import DATA_DIR


def test_chembl_file_exists():
    path = DATA_DIR / "herg_chembl.json"
    assert path.exists(), "ChEMBL hERG data file not found. Run src/chembl_downloader.py first."


def test_chembl_file_is_valid_json():
    path = DATA_DIR / "herg_chembl.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) > 0


def test_chembl_molecules_have_smiles():
    path = DATA_DIR / "herg_chembl.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for mol in data:
        assert "smiles" in mol
        assert isinstance(mol["smiles"], str)
        assert len(mol["smiles"]) > 0


def test_chembl_molecules_have_chembl_id():
    path = DATA_DIR / "herg_chembl.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for mol in data:
        assert "chembl_id" in mol
        assert mol["chembl_id"].startswith("CHEMBL")


def test_get_chembl_herg_smiles():
    from src.chembl_downloader import get_chembl_herg_smiles
    pairs = get_chembl_herg_smiles(min_pchembl=5.0)
    assert len(pairs) > 0
    for smi, label in pairs:
        assert isinstance(smi, str)
        assert label in (0, 1)
