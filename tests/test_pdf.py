import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.pdf_report import generate_pdf


def test_pdf_generate_russian():
    result = {
        "Solubility (logS)": -1.5,
        "SolubilityClass": "Soluble",
        "Caco-2 Permeability": 0.85,
        "Caco-2 Class": "High permeability",
        "hERG Toxicity Risk": 0.2,
        "hERG Class": "Low risk",
        "Lipophilicity (logD)": 2.5,
        "P-gp Inhibition": 0.1,
        "P-gp Class": "Non-inhibitor",
        "CYP3A4 Inhibition": 0.3,
        "CYP3A4 Class": "Non-inhibitor",
        "CYP2D6 Inhibition": 0.4,
        "CYP2D6 Class": "Non-inhibitor",
        "Ames Mutagenicity": 0.15,
        "Ames Class": "Non-mutagenic",
        "Bioavailability": 0.7,
        "Bioavailability Class": "High",
        "PPB (plasma binding)": 85.0,
        "PPB Class": "Strongly bound",
    }
    pdf = generate_pdf("CCO", result, "ru")
    assert isinstance(pdf, bytes)
    assert len(pdf) > 1000
    assert pdf[:5] == b"%PDF-"


def test_pdf_generate_english():
    result = {
        "Solubility (logS)": -1.5,
        "SolubilityClass": "Soluble",
        "Caco-2 Permeability": 0.97,
        "Caco-2 Class": "High permeability",
        "hERG Toxicity Risk": 0.8,
        "hERG Class": "High risk",
        "Lipophilicity (logD)": 3.2,
        "P-gp Inhibition": 0.9,
        "P-gp Class": "Inhibitor",
        "CYP3A4 Inhibition": 0.2,
        "CYP3A4 Class": "Non-inhibitor",
        "CYP2D6 Inhibition": 0.6,
        "CYP2D6 Class": "Inhibitor",
        "Ames Mutagenicity": 0.05,
        "Ames Class": "Non-mutagenic",
        "Bioavailability": 0.3,
        "Bioavailability Class": "Low",
        "PPB (plasma binding)": 95.0,
        "PPB Class": "Highly bound",
    }
    pdf = generate_pdf("CCO", result, "en")
    assert isinstance(pdf, bytes)
    assert len(pdf) > 1000
    assert pdf[:5] == b"%PDF-"


def test_pdf_with_partial_data():
    result = {
        "Solubility (logS)": -0.8,
        "Caco-2 Permeability": 0.75,
        "hERG Toxicity Risk": 0.1,
    }
    pdf = generate_pdf("CCO", result, "ru")
    assert isinstance(pdf, bytes)
    assert len(pdf) > 500
    assert pdf[:5] == b"%PDF-"
