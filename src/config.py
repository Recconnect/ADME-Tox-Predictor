import os
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"
TEST_DIR = BASE_DIR / "tests"

DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TEST_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("admetox")

PRIMARY_DATASETS = ["solubility", "caco2", "herg", "lipophilicity", "pgp"]

TDC_INFO = {
    "solubility": {"name": "AqSolDB", "task": "regression"},
    "caco2": {"name": "Caco2_Wang", "task": "classification"},
    "herg": {"name": "hERG", "task": "classification"},
    "lipophilicity": {"name": "Lipophilicity", "task": "regression"},
    "pgp": {"name": "Pgp_Broccatelli", "task": "classification"},
}

CACO2_THRESHOLD = -5.5

DATAVERSE_IDS = {
    "solubility": 4259610,
    "caco2": 4259569,
    "herg": 4259588,
    "lipophilicity": 4259595,
    "pgp": 4259597,
}

FINGERPRINT_PARAMS = {"radius": 2, "n_bits": 2048}
SCAFFOLD_SPLIT_PARAMS = {"test_size": 0.2, "val_size": 0.1, "seed": 42}

MODEL_PARAMS = {
    "solubility": {
        "n_estimators": 1000, "learning_rate": 0.05, "max_depth": 7,
        "num_leaves": 31, "subsample": 0.8, "colsample_bytree": 0.8,
        "reg_alpha": 0.1, "reg_lambda": 0.1, "min_child_samples": 20,
    },
    "caco2": {
        "n_estimators": 500, "learning_rate": 0.05, "max_depth": 5,
        "num_leaves": 31, "subsample": 0.8, "colsample_bytree": 0.8,
        "min_child_samples": 20,
    },
    "herg": {
        "n_estimators": 500, "learning_rate": 0.05, "max_depth": 5,
        "num_leaves": 31, "subsample": 0.8, "colsample_bytree": 0.8,
        "min_child_samples": 20,
    },
    "lipophilicity": {
        "n_estimators": 800, "learning_rate": 0.05, "max_depth": 6,
        "num_leaves": 31, "subsample": 0.8, "colsample_bytree": 0.8,
        "reg_alpha": 0.1, "reg_lambda": 0.1, "min_child_samples": 20,
    },
    "pgp": {
        "n_estimators": 500, "learning_rate": 0.05, "max_depth": 5,
        "num_leaves": 31, "subsample": 0.8, "colsample_bytree": 0.8,
        "min_child_samples": 20,
    },
}

BATCH_CHUNK_SIZE = 100
MAX_UPLOAD_MB = 50
MAX_BATCH_SIZE = 10000

VALIDATION_DRUGS = {
    "Aspirin": "CC(=O)Oc1ccccc1C(=O)O",
    "Ibuprofen": "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
    "Paracetamol": "CC(=O)Nc1ccc(O)cc1",
    "Metformin": "CN(C)C(=N)C(=N)N",
    "Atorvastatin": "O=C(O)C[C@H](O)C[C@H](O)CCn1c(c(c2ccccc2)c2ccccc2c1=O)C(=O)Nc1ccc(F)cc1",
    "Amoxicillin": "CC1(C(N2C(S1)C(C2=O)NC(=O)C(C3=CC=C(C=C3)O)N)C(=O)O)C",
    "Omeprazole": "CC1=CN=C(C(=N1)S(=O)C2=NC3=C(N2)C=C(C=C3)OC)C",
    "Caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    "Morphine": "CN1CC[C@]23[C@@H]4[C@H]1CC5=C2C(=C(C=C5)O)O[C@@H]3[C@H](C=C4)O",
    "Diazepam": "CN1C(=O)CN(C2=C1C=CC(=C2)Cl)C3=CC=CC=C3",
}
