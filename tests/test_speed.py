import time
import pytest
import numpy as np
from src.predict import ADMETPredictor

THRESHOLD_MS_SINGLE = 30.0
THRESHOLD_S_BATCH_1000 = 3.0
THRESHOLD_S_BATCH_100 = 0.5

SMILES_1000 = ["CCO"] * 1000
SMILES_VALIDATION = [
    "CC(=O)Oc1ccccc1C(=O)O",
    "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O",
    "CC(=O)Nc1ccc(O)cc1",
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    "CN(C)C(=N)N=C(N)N",
    "COc1ccc2c(c1)c(CC(=O)n1c(C)c(c3ccccc3C)n1)c(CC(=O)O)n2C",
] * 167


@pytest.fixture(scope="module")
def predictor():
    return ADMETPredictor()


def test_single_prediction_latency(predictor):
    times = []
    for _ in range(20):
        start = time.perf_counter()
        predictor.predict_single("CCO")
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
    median = np.median(times)
    assert median < THRESHOLD_MS_SINGLE, \
        f"Single prediction {median:.1f}ms > {THRESHOLD_MS_SINGLE}ms"


def test_batch_100_latency(predictor):
    start = time.perf_counter()
    results = predictor.predict_batch(SMILES_VALIDATION[:100])
    elapsed = time.perf_counter() - start
    assert len(results) == 100
    assert elapsed < THRESHOLD_S_BATCH_100, \
        f"Batch 100 took {elapsed:.2f}s > {THRESHOLD_S_BATCH_100}s"


def test_batch_1000_latency(predictor):
    start = time.perf_counter()
    results = predictor.predict_batch(SMILES_1000)
    elapsed = time.perf_counter() - start
    assert len(results) == 1000
    assert elapsed < THRESHOLD_S_BATCH_1000, \
        f"Batch 1000 took {elapsed:.2f}s > {THRESHOLD_S_BATCH_1000}s"


def test_warmup_speedup(predictor):
    cold_times = []
    for _ in range(3):
        start = time.perf_counter()
        predictor.predict_single("CCO")
        cold_times.append((time.perf_counter() - start) * 1000)
    warm_times = []
    for _ in range(10):
        start = time.perf_counter()
        predictor.predict_single("CCO")
        warm_times.append((time.perf_counter() - start) * 1000)
    cold_median = np.median(cold_times)
    warm_median = np.median(warm_times)
    assert warm_median < cold_median * 0.9, \
        f"Warmup not effective: cold {cold_median:.1f}ms, warm {warm_median:.1f}ms"


def test_throughput(predictor):
    """Measure predictions per second"""
    n = 50
    start = time.perf_counter()
    for _ in range(n):
        predictor.predict_single("CCO")
    elapsed = time.perf_counter() - start
    throughput = n / elapsed
    assert throughput > 30, \
        f"Throughput {throughput:.0f} pred/s too low (<30)"
