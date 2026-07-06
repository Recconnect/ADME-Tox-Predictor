import json
import numpy as np
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score, roc_auc_score

from src.config import MODELS_DIR, MODEL_PARAMS, TDC_INFO, CACO2_THRESHOLD, PRIMARY_DATASETS, logger
from src.data_loader import load_all_primary_datasets, save_datasets_info
from src.features import feature_pipeline
from src.models import (
    train_lightgbm_regression,
    train_lightgbm_classification,
    save_model,
)


def train_all_models():
    logger.info("=" * 60)
    logger.info("Step 1: Loading datasets")
    logger.info("=" * 60)
    datasets = load_all_primary_datasets()
    save_datasets_info(datasets)

    results = {}

    for key in PRIMARY_DATASETS:
        logger.info("=" * 60)
        logger.info("Step 2: Feature engineering for %s", key)
        logger.info("=" * 60)

        split = datasets[key]["split"]
        train_df = split["train"].copy()
        val_df = split["valid"].copy()
        test_df = split["test"].copy()

        if key == "caco2":
            logger.info("Binarizing Caco-2 at logPapp > %s", CACO2_THRESHOLD)
            for df_ in [train_df, val_df, test_df]:
                df_["Y"] = (df_["Y"] > CACO2_THRESHOLD).astype(int)
            logger.info("  Class distribution train: %s", train_df["Y"].value_counts().to_dict())

        logger.info("Computing features for train (%d)...", len(train_df))
        X_train, idx_train, feat_names = feature_pipeline(train_df["Drug"].values)
        y_train = train_df["Y"].values[idx_train]
        logger.info("X_train: %s", X_train.shape)

        logger.info("Computing features for val (%d)...", len(val_df))
        X_val, idx_val, _ = feature_pipeline(val_df["Drug"].values)
        y_val = val_df["Y"].values[idx_val]
        logger.info("X_val: %s", X_val.shape)

        logger.info("Computing features for test (%d)...", len(test_df))
        X_test, idx_test, _ = feature_pipeline(test_df["Drug"].values)
        y_test = test_df["Y"].values[idx_test]
        logger.info("X_test: %s", X_test.shape)

        logger.info("Step 3: Training %s...", key)
        task_type = TDC_INFO[key]["task"]
        params = MODEL_PARAMS.get(key, {})

        if task_type == "regression":
            model, metrics = train_lightgbm_regression(X_train, y_train, X_val, y_val, params)
        else:
            model, metrics = train_lightgbm_classification(X_train, y_train, X_val, y_val, params)

        metadata = {
            "key": key,
            "task": task_type,
            "feature_names": feat_names,
            "n_features": X_train.shape[1],
            "n_train": len(X_train),
            "n_val": len(X_val),
            "n_test": len(X_test),
        }
        model_path = MODELS_DIR / f"{key}_model.pkl"
        save_model(model, model_path, metadata=metadata)

        logger.info("Step 4: Evaluating test set...")
        if task_type == "regression":
            test_pred = model.predict(X_test)
            metrics["test_r2"] = float(r2_score(y_test, test_pred))
            metrics["test_mae"] = float(mean_absolute_error(y_test, test_pred))
            logger.info("  Test R2=%.4f, Test MAE=%.4f", metrics["test_r2"], metrics["test_mae"])
        else:
            test_pred = model.predict(X_test)
            test_prob = model.predict_proba(X_test)[:, 1]
            metrics["test_acc"] = float(accuracy_score(y_test, test_pred))
            metrics["test_auc"] = float(roc_auc_score(y_test, test_prob))
            logger.info("  Test Acc=%.4f, Test AUC=%.4f", metrics["test_acc"], metrics["test_auc"])

        results[key] = metrics

    results_path = MODELS_DIR / "training_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    logger.info("Results saved to %s", results_path)

    return results


if __name__ == "__main__":
    train_all_models()
