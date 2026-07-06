"""
Merge original hERG data with ChEMBL data and retrain model.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score

from src.config import DATA_DIR, MODELS_DIR, MODEL_PARAMS, logger
from src.data_loader import load_all_primary_datasets
from src.features import feature_pipeline, canonicalize_smiles
from src.models import train_lightgbm_classification, save_model
from src.chembl_downloader import get_chembl_herg_smiles


def merge_herg_data(min_pchembl: float = 5.0, datasets: dict | None = None) -> pd.DataFrame:
    if datasets is None:
        datasets = load_all_primary_datasets()
    orig_df = datasets["herg"]["data"].copy()
    orig_df = orig_df.rename(columns={"Y": "label"})

    n_orig = len(orig_df)
    logger.info("Original hERG: %d rows, %d toxic",
                n_orig, (orig_df["label"] == 1).sum())

    chembl_pairs = get_chembl_herg_smiles(min_pchembl=min_pchembl)
    if not chembl_pairs:
        return orig_df, datasets

    chembl_rows = []
    for smi, label in chembl_pairs:
        canon = canonicalize_smiles(smi)
        if canon:
            chembl_rows.append({"Drug": canon, "label": label})

    chembl_df = pd.DataFrame(chembl_rows).drop_duplicates(subset=["Drug"])
    logger.info("ChEMBL: %d rows, %d toxic", len(chembl_df), (chembl_df["label"] == 1).sum())

    existing = set(canonicalize_smiles(s) for s in orig_df["Drug"].dropna() if canonicalize_smiles(s))
    chembl_new = chembl_df[~chembl_df["Drug"].isin(existing)].copy()
    logger.info("ChEMBL new molecules: %d", len(chembl_new))

    if chembl_new.empty:
        return orig_df, datasets

    merged_df = pd.concat([orig_df, chembl_new], ignore_index=True)
    merged_df = merged_df.drop_duplicates(subset=["Drug"])
    merged_df = merged_df.reset_index(drop=True)
    logger.info("Merged hERG: %d rows (%d orig + %d new)",
                len(merged_df), n_orig, len(merged_df) - n_orig)

    new_datasets = dict(datasets)
    new_datasets["herg"] = {"data": merged_df.rename(columns={"label": "Y"}), "split": None}
    return merged_df, new_datasets


def retrain_herg(force_fetch: bool = False):
    from src.chembl_downloader import fetch_and_save_herg

    if force_fetch:
        fetch_and_save_herg(limit=200)

    datasets = load_all_primary_datasets()

    merged_df, merged_datasets = merge_herg_data(min_pchembl=5.0, datasets=datasets)
    data_df = merged_datasets["herg"]["data"]

    smiles_list = data_df["Drug"].tolist()
    labels = data_df["Y"].values

    X, valid_idx, feat_names = feature_pipeline(smiles_list, verbose=True)
    y = labels[valid_idx]

    logger.info("Feature matrix: %s, labels: %d pos / %d neg",
                X.shape, int(y.sum()), int((1 - y).sum()))

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    params = MODEL_PARAMS.get("herg", {})
    model, train_metrics = train_lightgbm_classification(X_train, y_train, X_test, y_test, params)

    test_pred = model.predict(X_test)
    test_prob = model.predict_proba(X_test)[:, 1]
    test_acc = float(accuracy_score(y_test, test_pred))
    test_auc = float(roc_auc_score(y_test, test_prob))

    logger.info("Expanded hERG test: Acc=%.4f, AUC=%.4f (n_train=%d, n_test=%d)",
                test_acc, test_auc, len(X_train), len(X_test))

    metadata = {
        "key": "herg",
        "task": "classification",
        "feature_names": feat_names,
        "n_features": X_train.shape[1],
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_original": len(datasets["herg"]["data"]),
        "n_chembl_added": len(merged_df) - len(datasets["herg"]["data"]),
        "test_acc": test_acc,
        "test_auc": test_auc,
    }

    model_path = MODELS_DIR / "herg_model_expanded.pkl"
    save_model(model, model_path, metadata=metadata)
    logger.info("Expanded model saved to %s", model_path)

    results = {"test_acc": test_acc, "test_auc": test_auc, "n_train": len(X_train), "n_test": len(X_test)}
    results_path = MODELS_DIR / "herg_expanded_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    logger.info("Results saved to %s", results_path)

    return model, results


if __name__ == "__main__":
    model, metrics = retrain_herg(force_fetch=False)
    print("Expanded hERG results:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
