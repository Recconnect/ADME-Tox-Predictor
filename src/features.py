import functools
import numpy as np
from rdkit import Chem

from src.config import logger, FINGERPRINT_PARAMS

_sanitize_ops = Chem.SANITIZE_ALL


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


@functools.lru_cache(maxsize=16384)
def _compute_rdkit_descriptors_cached(smiles: str) -> dict | None:
    mol = Chem.MolFromSmiles(smiles, sanitize=True)
    if mol is None or mol.GetNumAtoms() == 0:
        return None
    from rdkit.Chem import Descriptors, rdMolDescriptors

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


def compute_rdkit_descriptors(smiles: str) -> dict | None:
    canon = canonicalize_smiles(smiles)
    if canon is None:
        return None
    result = _compute_rdkit_descriptors_cached(canon)
    if result is None:
        return None
    return dict(result)


@functools.lru_cache(maxsize=16384)
def _morgan_fingerprint_cached(smiles: str) -> np.ndarray | None:
    mol = Chem.MolFromSmiles(smiles, sanitize=True)
    if mol is None or mol.GetNumAtoms() == 0:
        return None
    from rdkit.Chem import AllChem

    radius = FINGERPRINT_PARAMS["radius"]
    n_bits = FINGERPRINT_PARAMS["n_bits"]
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
    return np.array(fp, dtype=np.float32)


def get_morgan_fingerprint(smiles: str) -> np.ndarray | None:
    if not smiles or not smiles.strip():
        return None
    canon = canonicalize_smiles(smiles)
    if canon is None:
        return None
    result = _morgan_fingerprint_cached(canon)
    if result is None:
        return None
    return result.copy()


def compute_all_features(smiles: str) -> np.ndarray | None:
    desc = compute_rdkit_descriptors(smiles)
    fp = get_morgan_fingerprint(smiles)
    if desc is None or fp is None:
        return None
    desc_array = np.array(list(desc.values()), dtype=np.float32)
    return np.concatenate([desc_array, fp])


def get_descriptor_names() -> list[str]:
    result = compute_rdkit_descriptors("CCO")
    if result is None:
        return []
    return list(result.keys())


FEATURE_NAMES: list[str] | None = None


def get_feature_names() -> list[str]:
    global FEATURE_NAMES
    if FEATURE_NAMES is not None:
        return FEATURE_NAMES
    desc_names = get_descriptor_names()
    fp_names = [f"FP_{i}" for i in range(FINGERPRINT_PARAMS["n_bits"])]
    FEATURE_NAMES = desc_names + fp_names
    return FEATURE_NAMES


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
