from typing import Optional
import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    import dgl
    import dgl.nn as dglnn
    from dgl.utils import expand_as_pair
    DGL_AVAILABLE = True
except ImportError:
    DGL_AVAILABLE = False

from src.config import logger


class GINLayer(nn.Module):
    def __init__(self, in_dim: int, out_dim: int, dropout: float = 0.1):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(in_dim, out_dim),
            nn.BatchNorm1d(out_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(out_dim, out_dim),
            nn.BatchNorm1d(out_dim),
        )
        self.eps = nn.Parameter(torch.zeros(1))

    def forward(self, g, h, e=None):
        h_in = h
        with g.local_scope():
            g.ndata["h"] = h
            if e is not None:
                g.edata["e"] = e
            g.update_all(self._msg_fn, dgl.function.sum("m", "neigh"))
            h_neigh = g.ndata["neigh"]
            h_out = self.mlp((1 + self.eps) * h_in + h_neigh)
            return h_out

    @staticmethod
    def _msg_fn(edges):
        msg = edges.src["h"]
        if "e" in edges.data:
            msg = msg + edges.data["e"]
        return {"m": msg}


class GNNEncoder(nn.Module):
    def __init__(
        self,
        node_feat_dim: int,
        edge_feat_dim: int = 0,
        hidden_dim: int = 256,
        num_layers: int = 4,
        dropout: float = 0.1,
        use_checkpoint: bool = False,
    ):
        super().__init__()
        self.use_checkpoint = use_checkpoint
        self.node_embed = nn.Linear(node_feat_dim, hidden_dim)
        if edge_feat_dim > 0:
            self.edge_embed = nn.Linear(edge_feat_dim, hidden_dim)

        self.layers = nn.ModuleList()
        for i in range(num_layers):
            self.layers.append(
                GINLayer(hidden_dim, hidden_dim, dropout)
            )

        self.pool = dglnn.SumPooling()
        self.readout = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
        )
        self.edge_feat_dim = edge_feat_dim
        self.hidden_dim = hidden_dim

    def forward(self, g, h, e=None):
        h = self.node_embed(h)
        if e is not None and self.edge_feat_dim > 0:
            e = self.edge_embed(e)

        for layer in self.layers:
            if self.use_checkpoint and torch.is_grad_enabled():
                from torch.utils.checkpoint import checkpoint
                h = checkpoint(layer, g, h, e)
            else:
                h = layer(g, h, e)

        g.ndata["h"] = h
        out = self.pool(g, h)
        out = self.readout(out)
        return out


class GNNDropout(nn.Module):
    def __init__(self, p: float = 0.1):
        super().__init__()
        self.p = p

    def forward(self, x):
        if self.training and self.p > 0:
            mask = torch.empty_like(x).bernoulli_(1 - self.p)
            return x * mask / (1 - self.p)
        return x


class GNNPredictor(nn.Module):
    def __init__(
        self,
        node_feat_dim: int,
        edge_feat_dim: int = 0,
        hidden_dim: int = 256,
        num_layers: int = 4,
        num_tasks: int = 1,
        dropout: float = 0.1,
        use_checkpoint: bool = False,
    ):
        super().__init__()
        self.encoder = GNNEncoder(
            node_feat_dim=node_feat_dim,
            edge_feat_dim=edge_feat_dim,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            dropout=dropout,
            use_checkpoint=use_checkpoint,
        )
        self.head = nn.Linear(hidden_dim, num_tasks)

    def forward(self, g, h, e=None):
        emb = self.encoder(g, h, e)
        return self.head(emb)

    @torch.no_grad()
    def predict(self, g, h, e=None):
        self.eval()
        return self.forward(g, h, e)


class GradientCheckpointModule(nn.Module):
    def __init__(self, module: nn.Module):
        super().__init__()
        self.module = module

    def forward(self, *args):
        return self.module(*args)
