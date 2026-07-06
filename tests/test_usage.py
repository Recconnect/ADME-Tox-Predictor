import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.usage import log_prediction, get_stats, _DB_PATH


def setup_function():
    if _DB_PATH.exists():
        _DB_PATH.unlink()


def teardown_function():
    if _DB_PATH.exists():
        _DB_PATH.unlink()


def test_log_and_stats():
    log_prediction("alice", "CCO", "CCO", {"logS": -0.5}, None, 12.3)
    log_prediction("bob", "CC(=O)Oc1ccccc1C(=O)O", "CC(=O)Oc1ccccc1C(=O)O", {"logS": -2.1}, None, 8.7)
    log_prediction("alice", "INVALID", None, None, "bad SMILES", 0.5)
    log_prediction(None, "CCO", "CCO", {"logS": -0.5}, None, 15.0)

    stats = get_stats(30)
    assert stats["total_predictions"] == 4
    assert stats["errors"] == 1
    assert stats["unique_users"] == 2
    assert stats["unique_smiles"] == 3
    assert stats["predictions_7d"] == 4
    assert stats["avg_latency_ms"] > 0
    assert len(stats["top_users"]) == 2
    assert stats["top_users"][0]["username"] == "alice"


def test_empty_db():
    stats = get_stats(30)
    assert stats["total_predictions"] == 0
    assert stats["avg_latency_ms"] == 0
