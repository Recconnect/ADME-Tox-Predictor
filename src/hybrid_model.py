from typing import Optional
import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    import dgl
    DGL_AVAILABLE = True
except ImportError:
    DGL_AVAILABLE = False

from src.config import logger
from src.gnn import GNNEncoder
from src.gnn_features import graph_feature_dim, bond_feature_dim


class FusionHead(nn.Module):
    def __init__(
        self,
        gnn_dim: int,
        desc_dim: int,
        hidden_dim: int = 128,
        num_tasks: int = 1,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.fusion = nn.Sequential(
            nn.Linear(gnn_dim + desc_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_tasks),
        )

    def forward(self, gnn_emb: torch.Tensor, desc: torch.Tensor) -> torch.Tensor:
        x = torch.cat([gnn_emb, desc], dim=-1)
        return self.fusion(x)


class HybridModel(nn.Module):
    def __init__(
        self,
        desc_dim: int,
        node_feat_dim: Optional[int] = None,
        edge_feat_dim: Optional[int] = None,
        gnn_hidden_dim: int = 256,
        gnn_num_layers: int = 4,
        fusion_hidden_dim: int = 128,
        num_tasks: int = 1,
        dropout: float = 0.1,
        use_checkpoint: bool = False,
    ):
        super().__init__()
        self.use_checkpoint = use_checkpoint
        self.desc_dim = desc_dim

        if node_feat_dim is None:
            node_feat_dim = graph_feature_dim()
        if edge_feat_dim is None:
            edge_feat_dim = bond_feature_dim()

        self.gnn_encoder = GNNEncoder(
            node_feat_dim=node_feat_dim,
            edge_feat_dim=edge_feat_dim,
            hidden_dim=gnn_hidden_dim,
            num_layers=gnn_num_layers,
            dropout=dropout,
            use_checkpoint=use_checkpoint,
        )

        self.fusion_head = FusionHead(
            gnn_dim=gnn_hidden_dim,
            desc_dim=desc_dim,
            hidden_dim=fusion_hidden_dim,
            num_tasks=num_tasks,
            dropout=dropout,
        )

        self.lightgbm_bn = nn.BatchNorm1d(desc_dim)

    def forward(self, g, h, e, desc):
        gnn_emb = self.gnn_encoder(g, h, e)
        desc_norm = self.lightgbm_bn(desc)
        out = self.fusion_head(gnn_emb, desc_norm)
        return out

    def encode(self, g, h, e) -> torch.Tensor:
        return self.gnn_encoder(g, h, e)

    @torch.no_grad()
    def predict(self, g, h, e, desc):
        self.eval()
        return self.forward(g, h, e, desc)


class HybridMultiTask(nn.Module):
    def __init__(
        self,
        desc_dim: int,
        task_names: list[str],
        task_types: dict[str, str],
        node_feat_dim: Optional[int] = None,
        edge_feat_dim: Optional[int] = None,
        gnn_hidden_dim: int = 256,
        gnn_num_layers: int = 4,
        fusion_hidden_dim: int = 128,
        dropout: float = 0.1,
        use_checkpoint: bool = False,
    ):
        super().__init__()
        self.task_names = task_names
        self.task_types = task_types
        self.desc_dim = desc_dim

        if node_feat_dim is None:
            node_feat_dim = graph_feature_dim()
        if edge_feat_dim is None:
            edge_feat_dim = bond_feature_dim()

        self.gnn_encoder = GNNEncoder(
            node_feat_dim=node_feat_dim,
            edge_feat_dim=edge_feat_dim,
            hidden_dim=gnn_hidden_dim,
            num_layers=gnn_num_layers,
            dropout=dropout,
            use_checkpoint=use_checkpoint,
        )

        self.fusion_heads = nn.ModuleDict()
        for task_name in task_names:
            is_cls = task_types.get(task_name, "classification") == "classification"
            num_tasks = 1
            self.fusion_heads[task_name] = FusionHead(
                gnn_dim=gnn_hidden_dim,
                desc_dim=desc_dim,
                hidden_dim=fusion_hidden_dim,
                num_tasks=num_tasks,
                dropout=dropout,
            )

        self.lightgbm_bn = nn.BatchNorm1d(desc_dim)

    def forward(self, g, h, e, desc) -> dict[str, torch.Tensor]:
        gnn_emb = self.gnn_encoder(g, h, e)
        desc_norm = self.lightgbm_bn(desc)
        outputs = {}
        for task_name in self.task_names:
            outputs[task_name] = self.fusion_heads[task_name](gnn_emb, desc_norm)
        return outputs

    @torch.no_grad()
    def predict(self, g, h, e, desc) -> dict[str, torch.Tensor]:
        self.eval()
        return self.forward(g, h, e, desc)
