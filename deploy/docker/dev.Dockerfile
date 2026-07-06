FROM rocm/pytorch:rocm6.3_ubuntu22.04_py3.12_pytorch_release_2.4.0 AS dev

LABEL description="ADMETox.AI v3 development environment for AMD ROCm"
LABEL maintainer="ADMETox Team"

ENV DEBIAN_FRONTEND=noninteractive \
    ROCM_HOME=/opt/rocm \
    HSA_OVERRIDE_GFX_VERSION=10.3.0 \
    PYTORCH_ROCM_ARCH=gfx1030 \
    MIOPEN_FIND_ENFORCE=4 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    vim \
    curl \
    wget \
    rocm-dev \
    hip-dev \
    miopen-hip \
    rocblas \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    dgl \
    bitsandbytes==0.44.0 \
    onnx \
    onnxruntime-rocm \
    hydra-core \
    wandb \
    mlflow \
    pytorch-lightning \
    pytest \
    pytest-xdist \
    pytest-benchmark \
    pytest-timeout \
    memory-profiler \
    psutil \
    rdkit-pypi

RUN echo 'export PS1="\e[1;32m[ADMETox\e[0m \e[1;34m\w\e[0m\n\$ "' >> /root/.bashrc && \
    echo 'alias ll="ls -la"' >> /root/.bashrc && \
    echo 'alias train="python /workspace/adme_proto/train_hybrid.py"' >> /root/.bashrc && \
    echo 'alias test="python -m pytest /workspace/adme_proto/tests/ -v"' >> /root/.bashrc && \
    echo 'alias bench="python /workspace/adme_proto/tools/run_sota_benchmark.py"' >> /root/.bashrc

WORKDIR /workspace
ENTRYPOINT ["/workspace/adme_proto/deploy/docker/entrypoint.sh"]
CMD ["bash"]
