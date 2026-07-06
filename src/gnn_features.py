from typing import Optional
import numpy as np
from rdkit import Chem
from rdkit.Chem import rdchem

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import dgl
    DGL_AVAILABLE = True
except ImportError:
    DGL_AVAILABLE = False

from src.config import logger

ATOM_FEATURES = {
    "atomic_num": list(range(1, 101)),
    "degree": list(range(0, 6)),
    "formal_charge": list(range(-1, 3)),
    "num_hs": list(range(0, 5)),
    "hybridization": [
        rdchem.HybridizationType.SP,
        rdchem.HybridizationType.SP2,
        rdchem.HybridizationType.SP3,
        rdchem.HybridizationType.SP3D,
        rdchem.HybridizationType.SP3D2,
    ],
}

BOND_FEATURES = {
    "bond_type": [
        rdchem.BondType.SINGLE,
        rdchem.BondType.DOUBLE,
        rdchem.BondType.TRIPLE,
        rdchem.BondType.AROMATIC,
    ],
    "stereo": [
        rdchem.BondStereo.STEREONONE,
        rdchem.BondStereo.STEREOANY,
        rdchem.BondStereo.STEREOZ,
        rdchem.BondStereo.STEREOE,
        rdchem.BondStereo.STEREOCIS,
        rdchem.BondStereo.STEREOTRANS,
    ],
}


def _one_hot(val, choices):
    encoding = [0] * (len(choices) + 1)
    try:
        idx = choices.index(val)
    except (ValueError, IndexError):
        idx = -1
    if idx >= 0:
        encoding[idx] = 1
    else:
        encoding[-1] = 1
    return encoding


def _atom_features(atom):
    feats = []
    feats += _one_hot(atom.GetAtomicNum(), ATOM_FEATURES["atomic_num"])
    feats += _one_hot(atom.GetTotalDegree(), ATOM_FEATURES["degree"])
    feats += _one_hot(atom.GetFormalCharge(), ATOM_FEATURES["formal_charge"])
    feats += _one_hot(atom.GetTotalNumHs(), ATOM_FEATURES["num_hs"])
    feats += _one_hot(atom.GetHybridization(), ATOM_FEATURES["hybridization"])
    feats.append(int(atom.GetIsAromatic()))
    feats.append(float(atom.GetMass() * 0.01))
    return feats


def _bond_features(bond):
    feats = []
    feats += _one_hot(bond.GetBondType(), BOND_FEATURES["bond_type"])
    feats += _one_hot(bond.GetStereo(), BOND_FEATURES["stereo"])
    feats.append(int(bond.GetIsConjugated()))
    feats.append(int(bond.IsInRing()))
    return feats


def _require_torch():
    if not TORCH_AVAILABLE:
        raise ImportError("torch is required for GNN features. Install with: pip install torch")


def mol_to_graph(smiles: str) -> Optional["dgl.DGLGraph"]:
    if not DGL_AVAILABLE:
        raise ImportError("DGL is required for GNN features")
    _require_torch()
    import torch
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None

    atom_feats = []
    for atom in mol.GetAtoms():
        atom_feats.append(_atom_features(atom))

    src, dst = [], []
    bond_feats = []
    for bond in mol.GetBonds():
        u = bond.GetBeginAtomIdx()
        v = bond.GetEndAtomIdx()
        src.append(u)
        dst.append(v)
        src.append(v)
        dst.append(u)
        bond_feats.append(_bond_features(bond))
        bond_feats.append(_bond_features(bond))

    if not src:
        g = dgl.graph(([], []), num_nodes=len(mol.GetAtoms()))
    else:
        g = dgl.graph((src, dst), num_nodes=len(mol.GetAtoms()))

    g.ndata["h"] = torch.tensor(atom_feats, dtype=torch.float32)
    if bond_feats:
        g.edata["e"] = torch.tensor(bond_feats, dtype=torch.float32)
    return g


def graph_feature_dim() -> int:
    dummy = Chem.MolFromSmiles("CCO")
    if dummy is None:
        return 0
    feat = _atom_features(dummy.GetAtomWithIdx(0))
    return len(feat)


def bond_feature_dim() -> int:
    dummy = Chem.MolFromSmiles("CC")
    if dummy is None:
        return 0
    bond = dummy.GetBondWithIdx(0)
    return len(_bond_features(bond))


def node_feature_dim() -> int:
    return graph_feature_dim()
