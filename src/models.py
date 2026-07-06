from pathlib import Path
import numpy as np
import lightgbm as lgb
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score, roc_auc_score
from sklearn.model_selection import KFold, StratifiedKFold
import joblib

from src.config import logger

REGRESSION_DEFAULTS = {
    "n_estimators": 1000, "learning_rate": 0.05, "max_depth": 7,
    "num_leaves": 31, "subsample": 0.8, "colsample_bytree": 0.8,
    "reg_alpha": 0.1, "reg_lambda": 0.1, "min_child_samples": 20,
    "random_state": 42, "verbose": -1,
}

CLASSIFICATION_DEFAULTS = {
    "n_estimators": 500, "learning_rate": 0.05, "max_depth": 5,
    "num_leaves": 31, "subsample": 0.8, "colsample_bytree": 0.8,
    "min_child_samples": 20, "random_state": 42, "verbose": -1,
}

REGRESSION_GRID = {
    "n_estimators": [500, 800, 1000],
    "learning_rate": [0.01, 0.05, 0.1],
    "max_depth": [5, 7, 9],
    "reg_alpha": [0.01, 0.1, 1.0],
    "reg_lambda": [0.01, 0.1, 1.0],
}

CLASSIFICATION_GRID = {
    "n_estimators": [300, 500, 800],
    "learning_rate": [0.01, 0.05, 0.1],
    "max_depth": [3, 5, 7],
}


def _cv_score_regression(X, y, params, n_splits=5) -> dict:
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    scores = {"r2": [], "mae": []}
    for train_idx, val_idx in kf.split(X):
        X_tr, X_v = X[train_idx], X[val_idx]
        y_tr, y_v = y[train_idx], y[val_idx]
        m = lgb.LGBMRegressor(**params)
        m.fit(X_tr, y_tr, eval_set=[(X_v, y_v)], eval_metric="l2",
              callbacks=[lgb.early_stopping(20), lgb.log_evaluation(0)])
        p = m.predict(X_v)
        scores["r2"].append(float(r2_score(y_v, p)))
        scores["mae"].append(float(mean_absolute_error(y_v, p)))
    return {
        "cv_r2_mean": float(np.mean(scores["r2"])),
        "cv_r2_std": float(np.std(scores["r2"])),
        "cv_mae_mean": float(np.mean(scores["mae"])),
        "cv_mae_std": float(np.std(scores["mae"])),
    }


def _cv_score_classification(X, y, params, n_splits=5) -> dict:
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    scores = {"acc": [], "auc": []}
    for train_idx, val_idx in skf.split(X, y):
        X_tr, X_v = X[train_idx], X[val_idx]
        y_tr, y_v = y[train_idx], y[val_idx]
        m = lgb.LGBMClassifier(**params)
        m.fit(X_tr, y_tr, eval_set=[(X_v, y_v)], eval_metric="logloss",
              callbacks=[lgb.early_stopping(20), lgb.log_evaluation(0)])
        p = m.predict(X_v)
        prob = m.predict_proba(X_v)[:, 1]
        scores["acc"].append(float(accuracy_score(y_v, p)))
        scores["auc"].append(float(roc_auc_score(y_v, prob)))
    return {
        "cv_acc_mean": float(np.mean(scores["acc"])),
        "cv_acc_std": float(np.std(scores["acc"])),
        "cv_auc_mean": float(np.mean(scores["auc"])),
        "cv_auc_std": float(np.std(scores["auc"])),
    }


def _grid_search_params(X, y, grid, is_classification):
    best_params = None
    best_score = -float("inf")
    from itertools import product
    keys = list(grid.keys())
    for values in product(*grid.values()):
        candidate = dict(zip(keys, values))
        try:
            if is_classification:
                cv = _cv_score_classification(X, y, candidate, n_splits=3)
                score = cv["cv_auc_mean"]
            else:
                cv = _cv_score_regression(X, y, candidate, n_splits=3)
                score = cv["cv_r2_mean"]
            if score > best_score:
                best_score = score
                best_params = candidate
        except Exception as e:
            logger.warning("GridSearch combo failed: %s — %s", candidate, e)
    if best_params is None:
        best_params = {k: v[0] for k, v in grid.items()}
    logger.info("GridSearch best params: %s (score=%.4f)", best_params, best_score)
    return best_params


def train_lightgbm_regression(X_train, y_train, X_val, y_val, params=None, X_full=None, y_full=None, do_grid=False):
    if X_full is not None and y_full is not None and do_grid:
        grid_params = _grid_search_params(X_full, y_full, REGRESSION_GRID, is_classification=False)
        params = {**REGRESSION_DEFAULTS, **grid_params}
    elif params is None:
        params = dict(REGRESSION_DEFAULTS)

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

    if X_full is not None and y_full is not None:
        cv = _cv_score_regression(X_full, y_full, params)
        metrics.update(cv)

    logger.info(
        "Regression: Train R2=%.4f, Val R2=%.4f, Train MAE=%.4f, Val MAE=%.4f, best_iter=%d",
        metrics["train_r2"], metrics["val_r2"],
        metrics["train_mae"], metrics["val_mae"],
        metrics["best_iteration"],
    )
    return model, metrics


def train_lightgbm_classification(X_train, y_train, X_val, y_val, params=None, X_full=None, y_full=None, do_grid=False):
    if X_full is not None and y_full is not None and do_grid:
        grid_params = _grid_search_params(X_full, y_full, CLASSIFICATION_GRID, is_classification=True)
        params = {**CLASSIFICATION_DEFAULTS, **grid_params}
    elif params is None:
        params = dict(CLASSIFICATION_DEFAULTS)

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

    if X_full is not None and y_full is not None:
        cv = _cv_score_classification(X_full, y_full, params)
        metrics.update(cv)

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
