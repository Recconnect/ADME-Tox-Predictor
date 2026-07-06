import os
import json
import pandas as pd
import numpy as np
import requests
from sklearn.model_selection import train_test_split

from src.config import (
    DATA_DIR, DATAVERSE_IDS, PRIMARY_DATASETS,
    TDC_INFO, SCAFFOLD_SPLIT_PARAMS, logger,
)
from src.features import canonicalize_smiles


def download_tdc_dataset(dataset_key: str) -> pd.DataFrame:
    file_id = DATAVERSE_IDS.get(dataset_key)
    if file_id is None:
        raise ValueError(f"Unknown dataset: {dataset_key}")

    csv_path = DATA_DIR / f"{dataset_key}.tab"
    if csv_path.exists():
        logger.info("Loading cached file: %s", csv_path)
        df = pd.read_csv(csv_path, sep="\t")
    else:
        url = f"https://dataverse.harvard.edu/api/access/datafile/{file_id}"
        logger.info("Downloading from Harvard Dataverse: %s", url)
        resp = requests.get(url, timeout=120)
        if resp.status_code != 200:
            raise RuntimeError(
                f"Failed to download {dataset_key}: HTTP {resp.status_code}"
            )
        with open(csv_path, "wb") as f:
            f.write(resp.content)
        df = pd.read_csv(csv_path, sep="\t")
        logger.info("Saved %s (%d rows)", csv_path, len(df))

    if "Drug_ID" in df.columns:
        df = df.drop(columns=["Drug_ID"])
    if "Drug" not in df.columns and "SMILES" in df.columns:
        df = df.rename(columns={"SMILES": "Drug"})

    return df


def _sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(subset=["Drug"]).copy()
    df["Drug"] = df["Drug"].astype(str).str.strip()
    df = df[df["Drug"] != ""].copy()

    canon_list = []
    valid_mask = []
    for smi in df["Drug"]:
        c = canonicalize_smiles(smi)
        canon_list.append(c if c else None)
        valid_mask.append(c is not None)

    df["Drug"] = canon_list
    df = df[valid_mask].copy()
    df = df.drop_duplicates(subset=["Drug"]).reset_index(drop=True)
    return df


def scaffold_split(
    df: pd.DataFrame,
    smiles_col: str = "Drug",
    y_col: str = "Y",
    test_size: float = 0.2,
    val_size: float = 0.1,
    seed: int = 42,
):
    from rdkit import Chem
    from rdkit.Chem.AllChem import GetMorganFingerprintAsBitVect
    from sklearn.cluster import MiniBatchKMeans

    fps_list: list[np.ndarray] = []
    valid_indices: list[int] = []

    for i, smi in enumerate(df[smiles_col]):
        mol = Chem.MolFromSmiles(smi)
        if mol is not None:
            fp = GetMorganFingerprintAsBitVect(mol, 2, nBits=1024)
            fps_list.append(np.array(fp))
            valid_indices.append(i)

    df_valid = df.iloc[valid_indices].reset_index(drop=True)
    X_fp = np.array(fps_list)
    n_clusters = max(5, min(50, len(df_valid) // 20))
    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters, random_state=seed, batch_size=1024, n_init=3
    )
    clusters = kmeans.fit_predict(X_fp)
    df_valid = df_valid.copy()
    df_valid["cluster"] = clusters

    rng = np.random.RandomState(seed)
    total_size = len(df_valid)
    n_val = max(1, int(total_size * val_size))
    n_test = max(1, int(total_size * test_size))
    n_train = total_size - n_val - n_test

    def _try_stratified(indices, strat_labels, test_cnt, rs):
        try:
            tr, te = train_test_split(
                indices, test_size=min(test_cnt, len(indices) - 1),
                stratify=strat_labels, random_state=rs,
            )
            return tr, te
        except (ValueError, StopIteration):
            perm = rng.permutation(len(indices))
            split_pt = min(test_cnt, len(indices) - 1)
            te = np.array(indices)[perm[:split_pt]]
            tr = np.array(indices)[perm[split_pt:]]
            return tr.tolist(), te.tolist()

    all_idx = list(range(total_size))
    clusters_arr = df_valid["cluster"].values

    train_idx, temp_idx = _try_stratified(
        all_idx, clusters_arr, n_val + n_test, seed
    )

    temp_clusters = clusters_arr[temp_idx]
    n_temp = len(temp_idx)
    n_val_adj = min(n_val, n_temp - 1)
    n_test_adj = n_temp - n_val_adj

    v_idx, t_idx = _try_stratified(
        list(range(n_temp)), temp_clusters, n_test_adj, seed + 1
    )
    val_idx = np.array(temp_idx)[v_idx]
    test_idx = np.array(temp_idx)[t_idx]

    split = {
        "train": df_valid.iloc[train_idx].drop(columns=["cluster"]).reset_index(drop=True),
        "valid": df_valid.iloc[val_idx].drop(columns=["cluster"]).reset_index(drop=True),
        "test": df_valid.iloc[test_idx].drop(columns=["cluster"]).reset_index(drop=True),
    }
    return split


def load_tdc_dataset(dataset_key: str):
    df = download_tdc_dataset(dataset_key)
    logger.info("Raw %s: %d rows", dataset_key, len(df))
    df = _sanitize_dataframe(df)
    logger.info("After sanitization %s: %d unique valid molecules", dataset_key, len(df))
    split = scaffold_split(df)
    return df, split


def load_all_primary_datasets() -> dict:
    datasets = {}
    for key in PRIMARY_DATASETS:
        logger.info("Loading %s (%s)...", key, TDC_INFO[key]["name"])
        data, split = load_tdc_dataset(key)
        datasets[key] = {"data": data, "split": split}
        for split_name, sdf in split.items():
            logger.info("  %s: %d molecules", split_name, len(sdf))
    return datasets


def save_datasets_info(datasets: dict):
    info = {}
    for key, ds in datasets.items():
        split_info = {}
        for split_name, sdf in ds["split"].items():
            split_info[split_name] = {"count": len(sdf), "columns": list(sdf.columns)}
        info[key] = {
            "name": TDC_INFO[key]["name"],
            "task": TDC_INFO[key]["task"],
            "splits": split_info,
        }
    path = DATA_DIR / "datasets_info.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    logger.info("Dataset info saved to %s", path)


def get_dataset_stats(datasets: dict):
    for key in PRIMARY_DATASETS:
        split = datasets[key]["split"]
        for sname in ["train", "valid", "test"]:
            sdf = split[sname]
            logger.info(
                "%s %s: %d rows, Y range [%.3f, %.3f]",
                key, sname, len(sdf), sdf["Y"].min(), sdf["Y"].max(),
            )
