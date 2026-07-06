import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pytest
from sklearn.metrics import r2_score, accuracy_score, roc_auc_score

from src.models import (
    train_lightgbm_regression,
    train_lightgbm_classification,
    save_model,
    load_model,
)


class TestRegressionModel:
    def test_basic_regression(self):
        np.random.seed(42)
        n = 200
        X_train = np.random.randn(n, 10).astype(np.float32)
        y_train = X_train[:, 0] + 0.5 * X_train[:, 1] + np.random.randn(n) * 0.1
        X_val = np.random.randn(50, 10).astype(np.float32)
        y_val = X_val[:, 0] + 0.5 * X_val[:, 1] + np.random.randn(50) * 0.1

        model, metrics = train_lightgbm_regression(
            X_train, y_train, X_val, y_val,
            params={"n_estimators": 100, "random_state": 42, "verbose": -1},
        )
        assert metrics["val_r2"] > 0.5
        assert metrics["train_r2"] > 0.7

    def test_regression_predict_shape(self):
        np.random.seed(42)
        X_train = np.random.randn(100, 5).astype(np.float32)
        y_train = X_train[:, 0] * 2 + 1
        X_val = np.random.randn(20, 5).astype(np.float32)
        y_val = X_val[:, 0] * 2 + 1

        model, _ = train_lightgbm_regression(
            X_train, y_train, X_val, y_val,
            params={"n_estimators": 50, "random_state": 42, "verbose": -1},
        )
        pred = model.predict(X_val)
        assert pred.shape == (20,)
        assert np.all(np.isfinite(pred))


class TestClassificationModel:
    def test_basic_classification(self):
        np.random.seed(42)
        n = 200
        X_train = np.random.randn(n, 10).astype(np.float32)
        y_train = (X_train[:, 0] + X_train[:, 1] > 0).astype(int)
        X_val = np.random.randn(50, 10).astype(np.float32)
        y_val = (X_val[:, 0] + X_val[:, 1] > 0).astype(int)

        model, metrics = train_lightgbm_classification(
            X_train, y_train, X_val, y_val,
            params={"n_estimators": 100, "random_state": 42, "verbose": -1},
        )
        assert metrics["val_acc"] > 0.6
        assert metrics["train_acc"] > 0.7
        assert metrics["val_auc"] > 0.6
        assert metrics["train_auc"] > 0.7

    def test_classification_predict_proba(self):
        np.random.seed(42)
        X_train = np.random.randn(100, 5).astype(np.float32)
        y_train = (X_train[:, 0] > 0).astype(int)
        X_val = np.random.randn(20, 5).astype(np.float32)
        y_val = (X_val[:, 0] > 0).astype(int)

        model, _ = train_lightgbm_classification(
            X_train, y_train, X_val, y_val,
            params={"n_estimators": 50, "random_state": 42, "verbose": -1},
        )
        proba = model.predict_proba(X_val)
        assert proba.shape == (20, 2)
        assert np.all(proba >= 0) and np.all(proba <= 1)
        assert np.allclose(proba.sum(axis=1), 1.0)


class TestModelIO:
    def test_save_and_load(self, tmp_path):
        np.random.seed(42)
        X_train = np.random.randn(50, 5).astype(np.float32)
        y_train = np.random.randn(50)
        X_val = np.random.randn(10, 5).astype(np.float32)
        y_val = np.random.randn(10)

        model, _ = train_lightgbm_regression(
            X_train, y_train, X_val, y_val,
            params={"n_estimators": 20, "random_state": 42, "verbose": -1},
        )
        path = tmp_path / "test_model.pkl"
        save_model(model, path)
        assert path.exists()

        loaded = load_model(path)
        pred_orig = model.predict(X_val)
        pred_loaded = loaded.predict(X_val)
        np.testing.assert_array_equal(pred_orig, pred_loaded)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
