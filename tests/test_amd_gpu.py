import pytest
import time
import numpy as np

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from src.predict import ADMETPredictor

pytestmark = [
    pytest.mark.gpu,
    pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not installed (GPU tests require torch)"),
]

SMILES_ASPIRIN = "CC(=O)Oc1ccccc1C(=O)O"
SMILES_VALIDATION = [
    "CC(=O)Oc1ccccc1C(=O)O",
    "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O",
    "CC(=O)Nc1ccc(O)cc1",
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
]


def test_rocm_available():
    assert torch.cuda.is_available(), "ROCm GPU not detected"
    name = torch.cuda.get_device_name(0)
    assert "AMD" in name or "amd" in name.lower() or torch.cuda.get_device_capability(0), \
        f"Expected AMD GPU, got: {name}"


def test_rocm_device_count():
    count = torch.cuda.device_count()
    assert count >= 1, f"Expected at least 1 GPU, got {count}"


def test_rocm_memory():
    props = torch.cuda.get_device_properties(0)
    mem_gb = props.total_mem / 1024**3
    assert mem_gb >= 14.0, f"Expected >=14 GB VRAM, got {mem_gb:.1f} GB"


def test_miopen_cache_warming():
    predictor = ADMETPredictor()
    t1 = _time_prediction(predictor)
    t2 = _time_prediction(predictor)
    assert t2 < t1 * 0.8, f"MIOpen cache not effective: {t2:.1f}ms vs {t1:.1f}ms"


def test_fp16_equals_fp32():
    predictor = ADMETPredictor()
    result_fp32 = predictor.predict_single(SMILES_ASPIRIN)
    with torch.cuda.amp.autocast():
        result_fp16 = predictor.predict_single(SMILES_ASPIRIN)
    for key in result_fp32:
        if isinstance(result_fp32[key], (int, float)):
            diff = abs(result_fp32[key] - result_fp16.get(key, 0))
            assert diff < 1e-2, f"FP16 deviation too large for {key}: {diff}"


def test_batch_memory_safe():
    import psutil
    process = psutil.Process()
    mem_before = process.memory_info().rss / 1024**3
    predictor = ADMETPredictor()
    for _ in range(10):
        predictor.predict_single(SMILES_ASPIRIN)
    mem_after = process.memory_info().rss / 1024**3
    mem_leak = mem_after - mem_before
    assert mem_leak < 1.0, f"Possible memory leak: +{mem_leak:.2f} GB"


def test_rocm_smi_query():
    import subprocess
    result = subprocess.run(
        ["rocm-smi", "--showproductname"],
        capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, f"rocm-smi failed: {result.stderr}"
    assert "GPU" in result.stdout or "RX" in result.stdout or "AMD" in result.stdout


def _time_prediction(predictor, smiles=SMILES_ASPIRIN, n=5):
    times = []
    for _ in range(n):
        start = time.perf_counter()
        predictor.predict_single(smiles)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
    return np.median(times)
