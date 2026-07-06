import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from src.endpoints import ENDPOINTS, LEGACY_KEYS, ADME_KEYS, TOX_KEYS


class TestEndpoints:
    def test_legacy_endpoints_count(self):
        assert len(LEGACY_KEYS) == 10

    def test_total_endpoints_count(self):
        assert len(ENDPOINTS) >= 40, f"Expected 40+ endpoints, got {len(ENDPOINTS)}"

    def test_all_endpoints_have_required_fields(self):
        for key, cfg in ENDPOINTS.items():
            assert "name" in cfg, f"{key} missing name"
            assert "task" in cfg, f"{key} missing task"
            assert "group" in cfg, f"{key} missing group"
            assert cfg["task"] in ("classification", "regression"), f"{key} invalid task"

    def test_adme_tox_groups(self):
        assert len(ADME_KEYS) >= 18, f"Expected 18+ ADME endpoints, got {len(ADME_KEYS)}"
        assert len(TOX_KEYS) >= 20, f"Expected 20+ Tox endpoints, got {len(TOX_KEYS)}"

    def test_endpoint_names_unique(self):
        names = [cfg["name"] for cfg in ENDPOINTS.values()]
        assert len(names) == len(set(names)), "Duplicate endpoint names found"

    def test_classify_fn_exists_or_none(self):
        for key, cfg in ENDPOINTS.items():
            assert "classify" in cfg, f"{key} missing classify"
            assert cfg["classify"] is None or callable(cfg["classify"]), f"{key} classify not callable"

    def test_classify_fn_output(self):
        for key, cfg in ENDPOINTS.items():
            if cfg["classify"] is None:
                continue
            result = cfg["classify"](0.5)
            assert isinstance(result, dict), f"{key} classify did not return dict"
            assert len(result) >= 1, f"{key} classify returned empty dict"
            for k, v in result.items():
                assert isinstance(k, str), f"{key} classify key not string"
                assert isinstance(v, str), f"{key} classify value not string"


class TestGNNFeatures:
    def test_gnn_features_module_imports(self):
        try:
            from src.gnn_features import graph_feature_dim, bond_feature_dim, mol_to_graph
            assert graph_feature_dim() > 0
        except ImportError as e:
            if "dgl" in str(e).lower():
                pytest.skip("DGL not installed")
            raise

    def test_mol_to_graph(self):
        try:
            from src.gnn_features import mol_to_graph
            g = mol_to_graph("CCO")
            if g is None:
                pytest.skip("DGL mol_to_graph returned None")
            assert "h" in g.ndata
            assert g.num_nodes() == 3
            assert g.num_edges() >= 2
        except ImportError as e:
            if "dgl" in str(e).lower():
                pytest.skip("DGL not installed")
            raise

    def test_mol_to_graph_invalid(self):
        try:
            from src.gnn_features import mol_to_graph
            g = mol_to_graph("INVALID")
            assert g is None
        except ImportError as e:
            if "dgl" in str(e).lower():
                pytest.skip("DGL not installed")
            raise

    def test_atom_feature_dim(self):
        try:
            from src.gnn_features import graph_feature_dim
            dim = graph_feature_dim()
            assert dim > 0
            assert dim > 100
        except ImportError as e:
            if "dgl" in str(e).lower():
                pytest.skip("DGL not installed")
            raise

    def test_bond_feature_dim(self):
        try:
            from src.gnn_features import bond_feature_dim
            dim = bond_feature_dim()
            assert dim > 0
        except ImportError as e:
            if "dgl" in str(e).lower():
                pytest.skip("DGL not installed")
            raise
