import numpy as np
import pandas as pd

from src.features import get_feature_names
from src.models import load_model
from src.config import MODELS_DIR, logger


def get_model_feature_importance(model_key: str) -> list[dict] | None:
    path = MODELS_DIR / f"{model_key}_model.pkl"
    if not path.exists():
        logger.warning("Model not found: %s", path)
        return None
    model = load_model(path)
    if not hasattr(model, "feature_importances_"):
        return None

    importances = model.feature_importances_
    names = get_feature_names()

    n_desc = 30
    desc_importances = importances[:n_desc]
    fp_importances = importances[n_desc:]

    top_n = 10
    desc_indices = np.argsort(desc_importances)[-top_n:][::-1]
    fp_indices = np.argsort(fp_importances)[-top_n:][::-1]

    result = {
        "model": model_key,
        "descriptor_importance": [
            {"name": names[i], "importance": float(desc_importances[i])}
            for i in desc_indices
        ],
        "fingerprint_top_bits": [
            {"name": names[n_desc + i], "importance": float(fp_importances[i])}
            for i in fp_indices
        ],
        "fingerprint_total_importance": float(fp_importances.sum()),
        "descriptor_total_importance": float(desc_importances.sum()),
    }
    return result


def get_all_feature_importances() -> dict:
    result = {}
    for key in ["solubility", "caco2", "herg"]:
        imp = get_model_feature_importance(key)
        if imp:
            result[key] = imp
    return result


def format_importance_df(model_key: str) -> pd.DataFrame | None:
    data = get_model_feature_importance(model_key)
    if data is None:
        return None
    rows = data["descriptor_importance"]
    df = pd.DataFrame(rows)
    df.columns = ["Descriptor", "Importance"]
    df["Importance"] = df["Importance"].round(2)
    return df
