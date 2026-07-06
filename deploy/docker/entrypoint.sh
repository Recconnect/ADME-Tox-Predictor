#!/bin/bash
set -e

echo "============================================"
echo "  ADMETox.AI v3 - Development Environment"
echo "  ROCm $(cat /opt/rocm/.info/version 2>/dev/null || echo 'detected')"
echo "  PyTorch $(python -c 'import torch; print(torch.__version__)')"
echo "============================================"
echo ""

# Проверка ROCm
if [ -d /opt/rocm ]; then
    echo "[OK] ROCm found at /opt/rocm"
    rocm-smi --showproductname 2>/dev/null || echo "[WARN] rocm-smi not available"
else
    echo "[WARN] ROCm not found, running in CPU-only mode"
fi

# Проверка GPU
python -c "
import torch
if torch.cuda.is_available():
    name = torch.cuda.get_device_name(0)
    mem = torch.cuda.get_device_properties(0).total_mem / 1024**3
    print(f'[OK] GPU: {name} ({mem:.1f} GB VRAM)')
else:
    print('[INFO] No GPU detected, using CPU')
" 2>/dev/null || echo "[INFO] PyTorch GPU check skipped"

echo ""
exec "$@"
