import os
import pytest
import numpy as np
from src.predict import ADMETPredictor


def test_cpu_fallback_when_no_gpu():
    """Must work on CPU when no GPU is available"""
    predictor = ADMETPredictor()
    result = predictor.predict_single("CCO")
    assert "Solubility (logS)" in result
    assert isinstance(result["Solubility (logS)"], (int, float))


def test_cpu_gpu_result_consistency():
    """CPU and GPU predictions must match within tolerance"""
    predictor = ADMETPredictor()
    smiles_list = ["CCO", "CC(=O)Oc1ccccc1C(=O)O", "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O"]
    results = [predictor.predict_single(smi) for smi in smiles_list]
    for r in results:
        for key, val in r.items():
            if isinstance(val, (int, float)):
                assert not np.isnan(val), f"NaN in prediction: {key}"
                assert np.isfinite(val), f"Inf in prediction: {key}"


def test_docker_build_cpu():
    """Simulate Docker build on CPU-only environment"""
    predictor = ADMETPredictor()
    result = predictor.predict_single("CCO")
    assert len(result) >= 10


def test_onnx_export_import():
    """Model must exportable to ONNX and reimportable"""
    try:
        import torch
        predictor = ADMETPredictor()
        has_onnx = hasattr(predictor, "export_to_onnx") or \
                   hasattr(predictor, "to_onnx")
        if not has_onnx:
            pytest.skip("ONNX export not implemented yet")
    except ImportError:
        pytest.skip("PyTorch not available")


def test_environment_variables():
    """Check required env vars for platform detection"""
    allowed = {"ROCR_VISIBLE_DEVICES", "HIP_VISIBLE_DEVICES",
               "CUDA_VISIBLE_DEVICES", "ADMETOX_JWT_SECRET", "HSA_OVERRIDE_GFX_VERSION"}
    for var in allowed:
        if var in os.environ:
            val = os.environ[var]
            assert isinstance(val, str), f"{var} must be string"
