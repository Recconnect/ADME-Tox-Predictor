import functools
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, AllChem

from src.config import logger, FINGERPRINT_PARAMS


@functools.lru_cache(maxsize=65536)
def canonicalize_smiles(smiles: str) -> str | None:
    if not smiles or not smiles.strip():
        return None
    mol = Chem.MolFromSmiles(smiles, sanitize=True)
    if mol is None or mol.GetNumAtoms() == 0:
        return None
    return Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True)


def is_valid_smiles(smiles: str) -> bool:
    if not smiles or not smiles.strip():
        return False
    mol = Chem.MolFromSmiles(smiles, sanitize=True)
    return mol is not None and mol.GetNumAtoms() > 0


def _descriptors_from_mol(mol: Chem.Mol) -> dict:
    return {
        "MolWt": Descriptors.MolWt(mol),
        "LogP": Descriptors.MolLogP(mol),
        "NumHDonors": Descriptors.NumHDonors(mol),
        "NumHAcceptors": Descriptors.NumHAcceptors(mol),
        "TPSA": Descriptors.TPSA(mol),
        "NumRotatableBonds": Descriptors.NumRotatableBonds(mol),
        "FractionCSP3": rdMolDescriptors.CalcFractionCSP3(mol),
        "RingCount": Descriptors.RingCount(mol),
        "NumHeteroatoms": Descriptors.NumHeteroatoms(mol),
        "NumSaturatedRings": rdMolDescriptors.CalcNumSaturatedRings(mol),
        "NumAliphaticRings": rdMolDescriptors.CalcNumAliphaticRings(mol),
        "NumAromaticRings": rdMolDescriptors.CalcNumAromaticRings(mol),
        "NumSaturatedHeterocycles": rdMolDescriptors.CalcNumSaturatedHeterocycles(mol),
        "NumAliphaticHeterocycles": rdMolDescriptors.CalcNumAliphaticHeterocycles(mol),
        "NumAromaticHeterocycles": rdMolDescriptors.CalcNumAromaticHeterocycles(mol),
        "HeavyAtomCount": Descriptors.HeavyAtomCount(mol),
        "NHOHCount": Descriptors.NHOHCount(mol),
        "NOCount": Descriptors.NOCount(mol),
        "NumValenceElectrons": Descriptors.NumValenceElectrons(mol),
        "MaxPartialCharge": Descriptors.MaxPartialCharge(mol),
        "MinPartialCharge": Descriptors.MinPartialCharge(mol),
        "BalabanJ": Descriptors.BalabanJ(mol),
        "BertzCT": Descriptors.BertzCT(mol),
        "HallKierAlpha": Descriptors.HallKierAlpha(mol),
        "Ipc": Descriptors.Ipc(mol),
        "Kappa1": Descriptors.Kappa1(mol),
        "Kappa2": Descriptors.Kappa2(mol),
        "Kappa3": Descriptors.Kappa3(mol),
        "LabuteASA": Descriptors.LabuteASA(mol),
    }


def _fingerprint_from_mol(mol: Chem.Mol) -> np.ndarray:
    radius = FINGERPRINT_PARAMS["radius"]
    n_bits = FINGERPRINT_PARAMS["n_bits"]
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
    return np.array(fp, dtype=np.float32)


@functools.lru_cache(maxsize=32768)
def _compute_all_features_cached(smiles: str) -> np.ndarray | None:
    mol = Chem.MolFromSmiles(smiles, sanitize=True)
    if mol is None or mol.GetNumAtoms() == 0:
        return None
    desc = _descriptors_from_mol(mol)
    fp = _fingerprint_from_mol(mol)
    return np.concatenate([np.array(list(desc.values()), dtype=np.float32), fp])


@functools.lru_cache(maxsize=1)
def get_descriptor_names() -> list[str]:
    mol = Chem.MolFromSmiles("CCO", sanitize=True)
    if mol is None:
        return []
    return list(_descriptors_from_mol(mol).keys())


def compute_rdkit_descriptors(smiles: str) -> dict | None:
    feat = _compute_all_features_cached(smiles)
    if feat is None:
        return None
    names = get_descriptor_names()
    n = len(names)
    return dict(zip(names, feat[:n].tolist(), strict=False))


def get_morgan_fingerprint(smiles: str) -> np.ndarray | None:
    feat = _compute_all_features_cached(smiles)
    if feat is None:
        return None
    n = len(get_descriptor_names())
    return feat[n:].copy()


def compute_all_features(smiles: str) -> np.ndarray | None:
    result = _compute_all_features_cached(smiles)
    if result is None:
        return None
    return result.copy()


@functools.lru_cache(maxsize=1)
def get_feature_names() -> list[str]:
    desc_names = get_descriptor_names()
    fp_names = [f"FP_{i}" for i in range(FINGERPRINT_PARAMS["n_bits"])]
    return desc_names + fp_names


def feature_dimension() -> int:
    return len(get_feature_names())


def feature_pipeline(
    smiles_list: list[str],
    verbose: bool = True,
    chunk_size: int | None = None,
) -> tuple[np.ndarray, list[int], list[str]]:
    n = len(smiles_list)
    all_names = get_feature_names()
    X_list: list[np.ndarray] = []
    valid_indices: list[int] = []

    for i, smi in enumerate(smiles_list):
        if verbose and n > 100 and (i + 1) % 500 == 0:
            logger.info("Features computed: %d/%d", i + 1, n)
        feat = compute_all_features(smi)
        if feat is not None:
            X_list.append(feat)
            valid_indices.append(i)

    if not X_list:
        return np.array([], dtype=np.float32).reshape(0, len(all_names)), [], all_names

    X = np.array(X_list, dtype=np.float32)
    return X, valid_indices, all_names
