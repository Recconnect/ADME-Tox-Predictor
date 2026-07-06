"""All ADME/Tox endpoint definitions: 11 existing + 29 new = 40+."""

import numpy as np
from typing import Callable, Optional

EndpointConfig = dict

CLASSIFICATION_THRESHOLD = 0.5


def _ld50_classify(v: float) -> dict:
    log50 = np.log10(50)
    log500 = np.log10(500)
    if v < log50:
        return {"LD50 Class": "Highly toxic (<50 mg/kg)"}
    elif v < log500:
        return {"LD50 Class": "Moderately toxic (50-500 mg/kg)"}
    else:
        return {"LD50 Class": "Low toxicity (>500 mg/kg)"}


ENDPOINTS: dict[str, dict] = {
    # === Legacy 11 endpoints ===
    "solubility": {
        "name": "Solubility (logS)", "task": "regression",
        "source": "AqSolDB", "group": "ADME", "unit": "log mol/L",
        "classify": lambda v: {"SolubilityClass": "Soluble" if v > -4 else "Poorly soluble"},
    },
    "caco2": {
        "name": "Caco-2 Permeability", "task": "classification",
        "source": "Caco2_Wang", "group": "ADME", "unit": "binary",
        "classify": lambda v: {"Caco-2 Class": "High permeability" if v > 0.5 else "Low permeability"},
    },
    "herg": {
        "name": "hERG Toxicity Risk", "task": "classification",
        "source": "hERG", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"hERG Class": "Toxic (high risk)" if v > 0.5 else "Safe (low risk)"},
    },
    "lipophilicity": {
        "name": "Lipophilicity (logD)", "task": "regression",
        "source": "Lipophilicity", "group": "ADME", "unit": "log",
        "classify": None,
    },
    "pgp": {
        "name": "P-gp Inhibition", "task": "classification",
        "source": "Pgp_Broccatelli", "group": "ADME", "unit": "binary",
        "classify": lambda v: {"P-gp Class": "Inhibitor (high risk)" if v > 0.5 else "Non-inhibitor (low risk)"},
    },
    "cyp3a4": {
        "name": "CYP3A4 Inhibition", "task": "classification",
        "source": "CYP3A4_Veith", "group": "ADME", "unit": "binary",
        "classify": lambda v: {"CYP3A4 Class": "Inhibitor" if v > 0.5 else "Non-inhibitor"},
    },
    "cyp2d6": {
        "name": "CYP2D6 Inhibition", "task": "classification",
        "source": "CYP2D6_Veith", "group": "ADME", "unit": "binary",
        "classify": lambda v: {"CYP2D6 Class": "Inhibitor" if v > 0.5 else "Non-inhibitor"},
    },
    "ames": {
        "name": "Ames Mutagenicity", "task": "classification",
        "source": "Ames", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Ames Class": "Mutagenic (positive)" if v > 0.5 else "Non-mutagenic (negative)"},
    },
    "bioavailability": {
        "name": "Bioavailability", "task": "classification",
        "source": "Bioavailability_Ma", "group": "ADME", "unit": "binary",
        "classify": lambda v: {"Bioavailability Class": "High" if v > 0.5 else "Low"},
    },
    "ppbr": {
        "name": "PPB (plasma binding)", "task": "regression",
        "source": "PPBR_AZ", "group": "ADME", "unit": "%",
        "classify": lambda v: {"PPB Class": "Highly bound (>90%)" if v > 90 else "Moderately bound (50-90%)" if v > 50 else "Weakly bound (<50%)"},
    },

    # === New ADME endpoints ===
    "cyp2c9": {
        "name": "CYP2C9 Inhibition", "task": "classification",
        "source": "CYP2C9_Veith", "group": "ADME", "unit": "binary",
        "classify": lambda v: {"CYP2C9 Class": "Inhibitor" if v > 0.5 else "Non-inhibitor"},
    },
    "cyp2c19": {
        "name": "CYP2C19 Inhibition", "task": "classification",
        "source": "CYP2C19_Veith", "group": "ADME", "unit": "binary",
        "classify": lambda v: {"CYP2C19 Class": "Inhibitor" if v > 0.5 else "Non-inhibitor"},
    },
    "cyp2d6_substrate": {
        "name": "CYP2D6 Substrate", "task": "classification",
        "source": "CYP2D6_Substrate", "group": "ADME", "unit": "binary",
        "classify": lambda v: {"CYP2D6 Substrate": "Yes" if v > 0.5 else "No"},
    },
    "cyp3a4_substrate": {
        "name": "CYP3A4 Substrate", "task": "classification",
        "source": "CYP3A4_Substrate", "group": "ADME", "unit": "binary",
        "classify": lambda v: {"CYP3A4 Substrate": "Yes" if v > 0.5 else "No"},
    },
    "logd74": {
        "name": "logD7.4", "task": "regression",
        "source": "logD7.4", "group": "ADME", "unit": "log",
        "classify": None,
    },
    "fraction_unbound": {
        "name": "Fraction Unbound", "task": "regression",
        "source": "FractionUnbound", "group": "ADME", "unit": "fraction",
        "classify": lambda v: {"Fu Class": "Highly bound (<0.1)" if v < 0.1 else "Moderately bound (0.1-0.5)" if v < 0.5 else "Weakly bound (>0.5)"},
    },
    "mdck": {
        "name": "MDCK Permeability", "task": "classification",
        "source": "MDCK", "group": "ADME", "unit": "binary",
        "classify": lambda v: {"MDCK Class": "High permeability" if v > 0.5 else "Low permeability"},
    },
    "caco2_regression": {
        "name": "Caco-2 Permeability (regression)", "task": "regression",
        "source": "Caco2_Wang", "group": "ADME", "unit": "log Papp",
        "classify": None,
    },
    "half_life": {
        "name": "Half Life (T1/2)", "task": "regression",
        "source": "HalfLife", "group": "ADME", "unit": "hours",
        "classify": None,
    },
    "ddi": {
        "name": "Drug-Drug Interactions", "task": "classification",
        "source": "DDI", "group": "ADME", "unit": "binary",
        "classify": lambda v: {"DDI Risk": "High" if v > 0.5 else "Low"},
    },

    # === New Tox endpoints ===
    "tox21_ahr": {
        "name": "Tox21 AhR", "task": "classification",
        "source": "Tox21", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Tox21 AhR": "Active" if v > 0.5 else "Inactive"},
    },
    "tox21_ar": {
        "name": "Tox21 AR", "task": "classification",
        "source": "Tox21", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Tox21 AR": "Active" if v > 0.5 else "Inactive"},
    },
    "tox21_ar_ltk": {
        "name": "Tox21 AR-LBD", "task": "classification",
        "source": "Tox21", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Tox21 AR-LBD": "Active" if v > 0.5 else "Inactive"},
    },
    "tox21_aromatase": {
        "name": "Tox21 Aromatase", "task": "classification",
        "source": "Tox21", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Tox21 Aromatase": "Active" if v > 0.5 else "Inactive"},
    },
    "tox21_er": {
        "name": "Tox21 ER", "task": "classification",
        "source": "Tox21", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Tox21 ER": "Active" if v > 0.5 else "Inactive"},
    },
    "tox21_er_ltk": {
        "name": "Tox21 ER-LBD", "task": "classification",
        "source": "Tox21", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Tox21 ER-LBD": "Active" if v > 0.5 else "Inactive"},
    },
    "tox21_hse": {
        "name": "Tox21 HSE", "task": "classification",
        "source": "Tox21", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Tox21 HSE": "Active" if v > 0.5 else "Inactive"},
    },
    "tox21_mmgx": {
        "name": "Tox21 MMGx", "task": "classification",
        "source": "Tox21", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Tox21 MMGx": "Active" if v > 0.5 else "Inactive"},
    },
    "tox21_p53": {
        "name": "Tox21 p53", "task": "classification",
        "source": "Tox21", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Tox21 p53": "Active" if v > 0.5 else "Inactive"},
    },
    "tox21_pparg": {
        "name": "Tox21 PPARg", "task": "classification",
        "source": "Tox21", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Tox21 PPARg": "Active" if v > 0.5 else "Inactive"},
    },
    "tox21_aromatase2": {
        "name": "Tox21 Aromatase (alt)", "task": "classification",
        "source": "Tox21", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Tox21 Aromatase (alt)": "Active" if v > 0.5 else "Inactive"},
    },
    "tox21_fish": {
        "name": "Tox21 Fish", "task": "classification",
        "source": "Tox21", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Tox21 Fish": "Active" if v > 0.5 else "Inactive"},
    },
    "clintox": {
        "name": "ClinTox", "task": "classification",
        "source": "ClinTox", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"ClinTox": "Toxic" if v > 0.5 else "Non-toxic"},
    },
    "sider": {
        "name": "SIDER Side Effects", "task": "classification",
        "source": "SIDER", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"SIDER": "Side effects" if v > 0.5 else "No known side effects"},
    },
    "ld50": {
        "name": "LD50", "task": "regression",
        "source": "LD50", "group": "Tox", "unit": "log mg/kg",
        "classify": _ld50_classify,
    },
    "skin_sensitization": {
        "name": "Skin Sensitization", "task": "classification",
        "source": "SkinSens", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Skin Sensitization": "Sensitizer" if v > 0.5 else "Non-sensitizer"},
    },
    "eye_irritation": {
        "name": "Eye Irritation", "task": "classification",
        "source": "EyeIrr", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"Eye Irritation": "Irritant" if v > 0.5 else "Non-irritant"},
    },
    "herg_mutation": {
        "name": "hERG Mutation", "task": "classification",
        "source": "hERG_Mutation", "group": "Tox", "unit": "binary",
        "classify": lambda v: {"hERG Mutation Risk": "High" if v > 0.5 else "Low"},
    },
    "clearance": {
        "name": "Clearance (CL)", "task": "regression",
        "source": "Clearance", "group": "ADME", "unit": "mL/min/kg",
        "classify": lambda v: {"Clearance Class": "High (>10)" if v > 10 else "Moderate (3-10)" if v > 3 else "Low (<3)"},
    },
    "volume_distribution": {
        "name": "Volume of Distribution (Vd)", "task": "regression",
        "source": "VD", "group": "ADME", "unit": "L/kg",
        "classify": lambda v: {"Vd Class": "High (>5)" if v > 5 else "Moderate (1-5)" if v > 1 else "Low (<1)"},
    },
    "oral_absorption": {
        "name": "Oral Absorption", "task": "classification",
        "source": "OralAbsorption", "group": "ADME", "unit": "binary",
        "classify": lambda v: {"Oral Absorption": "Well absorbed (>30%)" if v > 0.5 else "Poorly absorbed (<30%)"},
    },
}

LEGACY_KEYS = [
    "solubility", "caco2", "herg", "lipophilicity", "pgp",
    "cyp3a4", "cyp2d6", "ames", "bioavailability", "ppbr",
]

ADME_KEYS = [k for k, v in ENDPOINTS.items() if v["group"] == "ADME"]
TOX_KEYS = [k for k, v in ENDPOINTS.items() if v["group"] == "Tox"]
CLASSIFICATION_KEYS = [k for k, v in ENDPOINTS.items() if v["task"] == "classification"]
REGRESSION_KEYS = [k for k, v in ENDPOINTS.items() if v["task"] == "regression"]


def get_endpoint_config(key: str) -> dict:
    return ENDPOINTS[key]


def get_task_type(key: str) -> str:
    return ENDPOINTS[key]["task"]


def get_endpoint_name(key: str) -> str:
    return ENDPOINTS[key]["name"]
