"""
Model export utilities: convert LightGBM pickles to deployable formats.

Usage:
    python -c "from src.export_models import export_all; export_all()"

Formats:
    - native_py: self-contained Python function via m2cgen (no deps)
    - json_dump: LightGBM model structure as JSON
"""

from pathlib import Path
import json

import m2cgen

from src.models import load_model
from src.config import MODELS_DIR, logger
from src.features import feature_dimension


def export_to_native_py(model, output_path: Path, model_name: str) -> bool:
    try:
        code = m2cgen.export_to_python(model)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# Auto-generated from {model_name} LightGBM model\n")
            f.write(f"# Feature dimension: {feature_dimension()}\n\n")
            f.write(code)
        logger.info("Exported %s -> %s", model_name, output_path)
        return True
    except Exception as e:
        logger.error("Failed to export %s: %s", model_name, e)
        return False


def export_to_json(model, output_path: Path, model_name: str) -> bool:
    try:
        booster = model.booster_
        dump = booster.dump_model()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(dump, f, indent=2)
        logger.info("Exported %s -> %s", model_name, output_path)
        return True
    except Exception as e:
        logger.error("Failed to dump %s: %s", model_name, e)
        return False


def export_all():
    n_features = feature_dimension()
    model_keys = [
        ("solubility", "solubility_model.pkl"),
        ("caco2", "caco2_model.pkl"),
        ("herg", "herg_model.pkl"),
        ("lipophilicity", "lipophilicity_model.pkl"),
        ("pgp", "pgp_model.pkl"),
        ("cyp3a4", "cyp3a4_model.pkl"),
        ("cyp2d6", "cyp2d6_model.pkl"),
        ("ames", "ames_model.pkl"),
        ("bioavailability", "bioavailability_model.pkl"),
        ("ppbr", "ppbr_model.pkl"),
    ]

    py_models = []
    json_models = []

    for key, pkl_name in model_keys:
        pkl_path = MODELS_DIR / pkl_name
        if not pkl_path.exists():
            logger.warning("Model %s not found at %s", key, pkl_path)
            continue

        model = load_model(pkl_path)

        py_path = MODELS_DIR / f"{key}_model.py"
        if export_to_native_py(model, py_path, key):
            py_models.append(key)

        json_path = MODELS_DIR / f"{key}_model.json"
        if export_to_json(model, json_path, key):
            json_models.append(key)

    # Also export expanded hERG
    herg_exp = MODELS_DIR / "herg_model_expanded.pkl"
    if herg_exp.exists():
        model = load_model(herg_exp)
        for out_name, ext in [("herg_expanded", "py"), ("herg_expanded", "json")]:
            out_path = MODELS_DIR / f"{out_name}_model.{ext}"
            if ext == "py":
                if export_to_native_py(model, out_path, "herg_expanded"):
                    py_models.append("herg_expanded")
            else:
                if export_to_json(model, out_path, "herg_expanded"):
                    json_models.append("herg_expanded")

    logger.info("Export complete: %d python + %d json", len(py_models), len(json_models))
    return {"python": py_models, "json": json_models}


if __name__ == "__main__":
    export_all()
