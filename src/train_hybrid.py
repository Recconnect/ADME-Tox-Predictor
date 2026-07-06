"""Phase A: LightGBM + GNN hybrid training pipeline."""

import json
import time
from pathlib import Path
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
from torch.cuda.amp import autocast, GradScaler

try:
    import dgl
    DGL_AVAILABLE = True
except ImportError:
    DGL_AVAILABLE = False

from src.config import MODELS_DIR, DATA_DIR, logger, PRIMARY_DATASETS
from src.data_loader import load_all_primary_datasets
from src.endpoints import ENDPOINTS, LEGACY_KEYS
from src.features import feature_pipeline, get_feature_names, feature_dimension
from src.gnn_features import mol_to_graph, graph_feature_dim, bond_feature_dim
from src.hybrid_model import HybridMultiTask, HybridModel
from src.models import save_model

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
AMP_ENABLED = torch.cuda.is_available()


def collate_hybrid(smiles_list: list[str], desc_array: np.ndarray):
    graphs = []
    features = []
    valid_indices = []
    for i, smi in enumerate(smiles_list):
        g = mol_to_graph(smi)
        if g is not None:
            graphs.append(g)
            features.append(desc_array[i])
            valid_indices.append(i)

    if not graphs:
        return None, None, None

    batched_graph = dgl.batch(graphs)
    batched_graph = batched_graph.to(DEVICE)
    desc_tensor = torch.tensor(np.array(features), dtype=torch.float32, device=DEVICE)
    return batched_graph, desc_tensor, valid_indices


def train_epoch(
    model: nn.Module,
    loader,
    optimizer: torch.optim.Optimizer,
    scaler: GradScaler,
    task_keys: list[str],
    task_types: dict[str, str],
    clip_norm: float = 1.0,
) -> dict:
    model.train()
    total_loss = 0.0
    task_losses = {k: 0.0 for k in task_keys}
    num_batches = 0

    for batched_graph, desc_tensor, targets in loader:
        batched_graph = batched_graph.to(DEVICE)
        desc_tensor = desc_tensor.to(DEVICE)
        targets = {k: t.to(DEVICE) for k, t in targets.items()}

        optimizer.zero_grad()

        with autocast(enabled=AMP_ENABLED):
            h = batched_graph.ndata["h"]
            e = batched_graph.edata.get("e")
            predictions = model(batched_graph, h, e, desc_tensor)

            loss = 0.0
            for k in task_keys:
                ttype = task_types.get(k, "classification")
                pred = predictions[k].squeeze(-1)
                target = targets[k].float()
                if ttype == "classification":
                    task_loss = nn.BCEWithLogitsLoss()(pred, target)
                else:
                    task_loss = nn.MSELoss()(pred, target)
                task_losses[k] += task_loss.item()
                loss += task_loss

        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        nn.utils.clip_grad_norm_(model.parameters(), clip_norm)
        scaler.step(optimizer)
        scaler.update()

        total_loss += loss.item()
        num_batches += 1

    avg_loss = total_loss / max(num_batches, 1)
    avg_task_losses = {k: v / max(num_batches, 1) for k, v in task_losses.items()}
    return {"loss": avg_loss, **avg_task_losses}


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader,
    task_keys: list[str],
    task_types: dict[str, str],
) -> dict:
    model.eval()
    total_loss = 0.0
    all_preds = {k: [] for k in task_keys}
    all_targets = {k: [] for k in task_keys}
    num_batches = 0

    for batched_graph, desc_tensor, targets in loader:
        batched_graph = batched_graph.to(DEVICE)
        desc_tensor = desc_tensor.to(DEVICE)
        targets = {k: t.to(DEVICE) for k, t in targets.items()}

        h = batched_graph.ndata["h"]
        e = batched_graph.edata.get("e")
        with autocast(enabled=AMP_ENABLED):
            predictions = model(batched_graph, h, e, desc_tensor)

        for k in task_keys:
            pred = predictions[k].squeeze(-1)
            target = targets[k].float()
            all_preds[k].append(pred.cpu())
            all_targets[k].append(target.cpu())

        num_batches += 1

    from sklearn.metrics import roc_auc_score, r2_score, accuracy_score

    metrics = {}
    for k in task_keys:
        preds = torch.cat(all_preds[k]).numpy()
        tgts = torch.cat(all_targets[k]).numpy()
        ttype = task_types.get(k, "classification")
        if ttype == "classification":
            probs = torch.sigmoid(torch.tensor(preds)).numpy()
            try:
                metrics[f"{k}_auc"] = float(roc_auc_score(tgts, probs))
            except Exception:
                metrics[f"{k}_auc"] = 0.0
            metrics[f"{k}_acc"] = float(accuracy_score(tgts, (probs > 0.5).astype(int)))
        else:
            try:
                metrics[f"{k}_r2"] = float(r2_score(tgts, preds))
            except Exception:
                metrics[f"{k}_r2"] = 0.0

    return metrics


class HybridDataset(torch.utils.data.Dataset):
    def __init__(self, smiles_list, desc_array, targets_dict):
        self.smiles = smiles_list
        self.desc = desc_array
        self.targets = targets_dict

    def __len__(self):
        return len(self.smiles)

    def __getitem__(self, idx):
        return self.smiles[idx], self.desc[idx], {k: v[idx] for k, v in self.targets.items()}


def hybrid_collate_fn(batch):
    smiles_list = [b[0] for b in batch]
    desc_array = np.array([b[1] for b in batch])
    targets = {k: torch.tensor([b[2][k] for b in batch], dtype=torch.float32) for k in batch[0][2].keys()}

    g = collate_hybrid(smiles_list, desc_array)
    if g[0] is None:
        return None
    return g[0], g[1], targets


def train_hybrid_models(
    task_keys: Optional[list[str]] = None,
    epochs: int = 100,
    batch_size: int = 128,
    lr: float = 1e-3,
    weight_decay: float = 1e-5,
    use_checkpoint: bool = False,
):
    if not DGL_AVAILABLE:
        raise ImportError("DGL is required for hybrid training. Install with: pip install dgl")

    if task_keys is None:
        task_keys = LEGACY_KEYS

    desc_dim = feature_dimension()
    node_dim = graph_feature_dim()
    edge_dim = bond_feature_dim()

    logger.info("=" * 60)
    logger.info("Phase A: LightGBM + GNN Hybrid Training")
    logger.info("Device: %s", DEVICE)
    logger.info("Tasks: %s", task_keys)
    logger.info("Descriptor dim: %d", desc_dim)
    logger.info("Node feature dim: %d", node_dim)
    logger.info("Edge feature dim: %d", edge_dim)
    logger.info("=" * 60)

    datasets = load_all_primary_datasets()
    task_types = {}
    for k in task_keys:
        task_types[k] = ENDPOINTS[k]["task"]

    train_data = {}
    for k in task_keys:
        split = datasets[k]["split"]
        smiles = split["train"]["Drug"].values
        y = split["train"]["Y"].values
        train_data[k] = (smiles, y)

    model = HybridMultiTask(
        desc_dim=desc_dim,
        task_names=task_keys,
        task_types=task_types,
        node_feat_dim=node_dim,
        edge_feat_dim=edge_dim,
        gnn_hidden_dim=256,
        gnn_num_layers=4,
        fusion_hidden_dim=128,
        dropout=0.1,
        use_checkpoint=use_checkpoint,
    ).to(DEVICE)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=10
    )
    scaler = GradScaler(enabled=AMP_ENABLED)

    logger.info("Precomputing features and graphs before training...")

    all_smiles_list = train_data[task_keys[0]][0]
    all_smiles_list = all_smiles_list.tolist() if hasattr(all_smiles_list, 'tolist') else list(all_smiles_list)
    desc_array, valid_idx, _ = feature_pipeline(all_smiles_list, verbose=True)
    desc_array = desc_array.astype(np.float32)
    all_smiles_list = [all_smiles_list[i] for i in valid_idx]
    n_valid = len(all_smiles_list)

    targets_dict = {}
    for k in task_keys:
        y = np.array(train_data[k][1], dtype=np.float32)
        targets_dict[k] = y[valid_idx]

    logger.info("Precomputing DGL graphs (%d molecules)...", n_valid)
    cached_graphs: list = [None] * n_valid
    for i, smi in enumerate(all_smiles_list):
        if (i + 1) % 500 == 0:
            logger.info("  Graphs: %d/%d", i + 1, n_valid)
        cached_graphs[i] = mol_to_graph(smi)

    valid_graph_idx = [i for i, g in enumerate(cached_graphs) if g is not None]
    all_smiles_list = [all_smiles_list[i] for i in valid_graph_idx]
    desc_array = desc_array[valid_graph_idx]
    for k in task_keys:
        targets_dict[k] = targets_dict[k][valid_graph_idx]
    cached_graphs = [cached_graphs[i] for i in valid_graph_idx]

    logger.info("Training on %d molecules with valid graphs", len(all_smiles_list))

    dataset = HybridDataset(all_smiles_list, desc_array, targets_dict)
    loader = torch.utils.data.DataLoader(
        dataset, batch_size=batch_size, shuffle=True,
        collate_fn=hybrid_collate_fn, drop_last=True,
    )

    best_loss = float("inf")
    patience = 20
    patience_counter = 0

    for epoch in range(epochs):
        logger.info("Epoch %d/%d", epoch + 1, epochs)

        loader.dataset = HybridDataset(all_smiles_list, desc_array, targets_dict)

        train_metrics = train_epoch(
            model, loader, optimizer, scaler, task_keys, task_types
        )
        logger.info("  Train loss: %.4f", train_metrics["loss"])

        scheduler.step(train_metrics["loss"])
        current_lr = optimizer.param_groups[0]["lr"]
        logger.info("  LR: %.6f", current_lr)

        if train_metrics["loss"] < best_loss:
            best_loss = train_metrics["loss"]
            patience_counter = 0
            torch.save(model.state_dict(), MODELS_DIR / "hybrid_best.pt")
            logger.info("  New best model saved (loss=%.4f)", best_loss)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info("Early stopping at epoch %d", epoch + 1)
                break

    model.load_state_dict(torch.load(MODELS_DIR / "hybrid_best.pt", weights_only=True))
    logger.info("Training complete. Best loss: %.4f", best_loss)

    save_path = MODELS_DIR / "hybrid_model.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "task_keys": task_keys,
            "task_types": task_types,
            "desc_dim": desc_dim,
            "node_feat_dim": node_dim,
            "edge_feat_dim": edge_dim,
            "best_loss": best_loss,
        },
        save_path,
    )
    logger.info("Hybrid model saved to %s", save_path)
    return model


if __name__ == "__main__":
    train_hybrid_models()
