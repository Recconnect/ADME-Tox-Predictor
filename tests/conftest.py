import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "gpu: mark test as requiring AMD ROCm GPU"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow (weekly run)"
    )
    config.addinivalue_line(
        "markers",
        "benchmark: mark test as benchmark (weekly run)"
    )


def pytest_collection_modifyitems(config, items):
    skip_gpu = not config.getoption("--gpu")
    skip_slow = not config.getoption("--slow")

    for item in items:
        if skip_gpu and "gpu" in item.keywords:
            item.add_marker(
                pytest.mark.skip(reason="use --gpu to run GPU tests")
            )
        if skip_slow and "slow" in item.keywords:
            item.add_marker(
                pytest.mark.skip(reason="use --slow to run slow tests")
            )
        if "benchmark" in item.keywords and not config.getoption("--benchmark"):
            item.add_marker(
                pytest.mark.skip(reason="use --benchmark to run benchmarks")
            )


def pytest_addoption(parser):
    parser.addoption(
        "--gpu", action="store_true", default=False,
        help="run GPU tests (requires AMD ROCm)"
    )
    parser.addoption(
        "--slow", action="store_true", default=False,
        help="run slow tests (weekly)"
    )
    parser.addoption(
        "--benchmark", action="store_true", default=False,
        help="run benchmark tests"
    )
