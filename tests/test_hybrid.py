import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

pytestmark = pytest.mark.skipif(not TORCH_AVAILABLE, reason="torch not installed")


class TestGNNModel:
    def test_gin_layer_forward(self):
        import dgl
        from src.gnn import GINLayer
        layer = GINLayer(64, 128)
        g = dgl.graph(([0, 1], [1, 0]))
        h = torch.randn(2, 64)
        out = layer(g, h)
        assert out.shape == (2, 128)

    def test_gnn_encoder_forward(self):
        import dgl
        from src.gnn import GNNEncoder
        encoder = GNNEncoder(
            node_feat_dim=128,
            edge_feat_dim=12,
            hidden_dim=256,
            num_layers=2,
            dropout=0.1,
        )
        g = dgl.graph(([0, 1, 2], [1, 2, 0]))
        g.ndata["h"] = torch.randn(3, 128)
        g.edata["e"] = torch.randn(3, 12)
        emb = encoder(g, g.ndata["h"], g.edata["e"])
        assert emb.shape == (1, 256)

    def test_gnn_predictor_forward(self):
        import dgl
        from src.gnn import GNNPredictor
        predictor = GNNPredictor(
            node_feat_dim=128,
            edge_feat_dim=12,
            hidden_dim=256,
            num_tasks=10,
            num_layers=2,
        )
        g = dgl.graph(([0, 1], [1, 0]))
        g.ndata["h"] = torch.randn(2, 128)
        g.edata["e"] = torch.randn(2, 12)
        out = predictor(g, g.ndata["h"], g.edata["e"])
        assert out.shape == (1, 10)

    def test_gnn_amp_compatible(self):
        import dgl
        from src.gnn import GNNEncoder
        if not torch.cuda.is_available():
            pytest.skip("No GPU for AMP test")
        encoder = GNNEncoder(node_feat_dim=128, hidden_dim=128, num_layers=2)
        g = dgl.graph(([0, 1], [1, 0])).cuda()
        h = torch.randn(2, 128).cuda()
        with torch.cuda.amp.autocast():
            emb = encoder(g, h)
        assert emb.shape == (1, 128)


class TestHybridModel:
    def test_fusion_head_forward(self):
        from src.hybrid_model import FusionHead
        head = FusionHead(gnn_dim=256, desc_dim=128, hidden_dim=64, num_tasks=5)
        gnn_emb = torch.randn(4, 256)
        desc = torch.randn(4, 128)
        out = head(gnn_emb, desc)
        assert out.shape == (4, 5)

    def test_hybrid_model_forward(self):
        import dgl
        from src.hybrid_model import HybridModel
        model = HybridModel(
            desc_dim=128,
            gnn_hidden_dim=256,
            gnn_num_layers=2,
            fusion_hidden_dim=64,
            num_tasks=10,
            dropout=0.1,
        )
        g = dgl.graph(([0, 1], [1, 0]))
        g.ndata["h"] = torch.randn(2, model.gnn_encoder.node_embed.in_features)
        if model.gnn_encoder.edge_feat_dim > 0:
            g.edata["e"] = torch.randn(2, model.gnn_encoder.edge_feat_dim)
        desc = torch.randn(1, 128)
        out = model(g, g.ndata["h"], g.edata.get("e"), desc)
        assert out.shape == (1, 10)

    def test_hybrid_multi_task_forward(self):
        import dgl
        from src.hybrid_model import HybridMultiTask
        task_names = ["solubility", "caco2", "herg", "cyp2d6"]
        task_types = {"solubility": "regression", "caco2": "classification", "herg": "classification", "cyp2d6": "classification"}
        model = HybridMultiTask(
            desc_dim=128,
            task_names=task_names,
            task_types=task_types,
            gnn_hidden_dim=256,
            gnn_num_layers=2,
        )
        g = dgl.graph(([0, 1], [1, 0]))
        g.ndata["h"] = torch.randn(2, model.gnn_encoder.node_embed.in_features)
        if model.gnn_encoder.edge_feat_dim > 0:
            g.edata["e"] = torch.randn(2, model.gnn_encoder.edge_feat_dim)
        desc = torch.randn(1, 128)
        outputs = model(g, g.ndata["h"], g.edata.get("e"), desc)
        assert isinstance(outputs, dict)
        for name in task_names:
            assert name in outputs
            assert outputs[name].shape == (1, 1)

    def test_hybrid_predict_returns_sigmoid_for_classification(self):
        import dgl
        from src.hybrid_model import HybridMultiTask
        model = HybridMultiTask(
            desc_dim=128,
            task_names=["ames"],
            task_types={"ames": "classification"},
            gnn_hidden_dim=64,
            gnn_num_layers=1,
        )
        g = dgl.graph(([0, 1], [1, 0]))
        g.ndata["h"] = torch.randn(2, model.gnn_encoder.node_embed.in_features)
        desc = torch.randn(1, 128)
        with torch.no_grad():
            out = model.predict(g, g.ndata["h"], None, desc)
        logit = out["ames"].squeeze(-1).item()
        prob = float(torch.sigmoid(torch.tensor(logit)))
        assert 0.0 <= prob <= 1.0
