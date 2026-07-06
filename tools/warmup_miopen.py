"""
MIOpen kernel cache warmup for AMD ROCm.
Run once after container start to avoid cold-start latency.
"""
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch
from src.predict import ADMETPredictor

WARMUP_SMILES = [
    "CCO",
    "CC(=O)Oc1ccccc1C(=O)O",
    "CC(C)Cc1ccc(cc1)[C@@H](C)C(=O)O",
    "CC(=O)Nc1ccc(O)cc1",
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
    "CN(C)C(=N)N=C(N)N",
    "COc1ccc2c(c1)c(CC(=O)n1c(C)c(c3ccccc3C)n1)c(CC(=O)O)n2C",
    "c1ccccc1",
    "c1ccc2c(c1)c3ccccc3[nH]2",
    "CCCO",
]


def warmup():
    print("MIOpen Kernel Cache Warmup")
    print("=" * 40)
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB")

    print("\nLoading predictor...")
    predictor = ADMETPredictor()
    print("Done.\n")

    print("Warming up MIOpen kernels...")
    total_start = time.time()
    for i, smiles in enumerate(WARMUP_SMILES, 1):
        start = time.time()
        predictor.predict_single(smiles)
        elapsed = (time.time() - start) * 1000
        print(f"  [{i}/{len(WARMUP_SMILES)}] {smiles[:30]:30s} {elapsed:7.1f} ms")

    total = (time.time() - total_start) * 1000
    print(f"\nWarmup complete in {total:.0f} ms")
    print("MIOpen kernels are now cached.")

    if torch.cuda.is_available():
        mem = torch.cuda.memory_allocated() / 1024**3
        print(f"VRAM after warmup: {mem:.2f} GB")


if __name__ == "__main__":
    warmup()
