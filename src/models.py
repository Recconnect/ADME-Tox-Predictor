from pathlib import Path
import numpy as np
import lightgbm as lgb
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score, roc_auc_score
import joblib

from src.config import logger


def train_lightgbm_regression(X_train, y_train, X_val, y_val, params=None):
    if params is None:
        params = {
            "n_estimators": 1000, "learning_rate": 0.05, "max_depth": 7,
            "num_leaves": 31, "subsample": 0.8, "colsample_bytree": 0.8,
            "reg_alpha": 0.1, "reg_lambda": 0.1, "min_child_samples": 20,
            "random_state": 42, "verbose": -1,
        }

    model = lgb.LGBMRegressor(**params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        eval_metric="l2",
        callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)],
    )

    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)

    metrics = {
        "train_r2": float(r2_score(y_train, train_pred)),
        "val_r2": float(r2_score(y_val, val_pred)),
        "train_mae": float(mean_absolute_error(y_train, train_pred)),
        "val_mae": float(mean_absolute_error(y_val, val_pred)),
        "best_iteration": model.best_iteration_,
    }

    logger.info(
        "Regression: Train R2=%.4f, Val R2=%.4f, Train MAE=%.4f, Val MAE=%.4f, best_iter=%d",
        metrics["train_r2"], metrics["val_r2"],
        metrics["train_mae"], metrics["val_mae"],
        metrics["best_iteration"],
    )
    return model, metrics


def train_lightgbm_classification(X_train, y_train, X_val, y_val, params=None):
    if params is None:
        params = {
            "n_estimators": 500, "learning_rate": 0.05, "max_depth": 5,
            "num_leaves": 31, "subsample": 0.8, "colsample_bytree": 0.8,
            "min_child_samples": 20, "random_state": 42, "verbose": -1,
        }

    model = lgb.LGBMClassifier(**params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        eval_metric="logloss",
        callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)],
    )

    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)
    train_prob = model.predict_proba(X_train)[:, 1]
    val_prob = model.predict_proba(X_val)[:, 1]

    metrics = {
        "train_acc": float(accuracy_score(y_train, train_pred)),
        "val_acc": float(accuracy_score(y_val, val_pred)),
        "train_auc": float(roc_auc_score(y_train, train_prob)),
        "val_auc": float(roc_auc_score(y_val, val_prob)),
        "best_iteration": model.best_iteration_,
    }

    logger.info(
        "Classification: Train Acc=%.4f, Val Acc=%.4f, Train AUC=%.4f, Val AUC=%.4f, best_iter=%d",
        metrics["train_acc"], metrics["val_acc"],
        metrics["train_auc"], metrics["val_auc"],
        metrics["best_iteration"],
    )
    return model, metrics


def save_model(model, model_path, metadata=None):
    path = Path(model_path) if isinstance(model_path, str) else model_path
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "metadata": metadata or {}}, path)
    logger.info("Model saved to %s", path)
    return path


def load_model(model_path):
    data = joblib.load(model_path)
    if isinstance(data, dict) and "model" in data:
        return data["model"]
    return data
