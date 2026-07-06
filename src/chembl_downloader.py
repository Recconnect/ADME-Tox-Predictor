"""
ChEMBL API client for expanding ADME/Tox datasets.

Использует публичный ChEMBL API без авторизации.
Запросы идут через https://www.ebi.ac.uk/chembl/api/data
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests
import time
from src.config import DATA_DIR, logger


CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"
REQUEST_DELAY = 0.5


def _get_json(url: str, params: dict | None = None) -> dict | None:
    time.sleep(REQUEST_DELAY)
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        logger.warning("ChEMBL API error: HTTP %s for %s", resp.status_code, url)
        return None
    except requests.RequestException as e:
        logger.warning("ChEMBL API request failed: %s", e)
        return None


def search_herg_assays(limit: int = 100) -> list[dict]:
    """
    Ищет hERG (KCNH2) assay data в ChEMBL.
    Использует canonical_smiles из ответа API (без доп. запросов к молекулам).
    """
    target_chembl_id = "CHEMBL240"
    logger.info("Using hERG target: %s", target_chembl_id)

    offset = 0
    all_molecules = []
    seen_chembl_ids = set()

    while len(all_molecules) < limit:
        assay_query = (
            f"{CHEMBL_BASE}/activity.json"
            f"?target_chembl_id={target_chembl_id}"
            f"&limit=100&offset={offset}"
        )
        assay_data = _get_json(assay_query)
        if not assay_data or "activities" not in assay_data or not assay_data["activities"]:
            break

        for act in assay_data["activities"]:
            mol_chembl_id = act.get("molecule_chembl_id")
            if not mol_chembl_id or mol_chembl_id in seen_chembl_ids:
                continue
            seen_chembl_ids.add(mol_chembl_id)

            smiles = act.get("canonical_smiles") or ""
            if not smiles:
                continue

            standard_type = act.get("standard_type") or ""
            if not standard_type:
                continue

            all_molecules.append({
                "smiles": smiles,
                "chembl_id": mol_chembl_id,
                "standard_value": act.get("standard_value"),
                "standard_units": act.get("standard_units"),
                "standard_type": standard_type,
                "pchembl_value": act.get("pchembl_value"),
            })

            if len(all_molecules) >= limit:
                break

        offset += 100
        logger.info("Fetched %d molecules so far (offset=%d)", len(all_molecules), offset)

    logger.info("Found %d hERG molecules from ChEMBL", len(all_molecules))
    return all_molecules


def fetch_and_save_herg(limit: int = 500) -> str:
    molecules = search_herg_assays(limit=limit)
    if not molecules:
        logger.warning("No hERG data fetched from ChEMBL")
        return ""

    import json
    path = DATA_DIR / "herg_chembl.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(molecules, f, indent=2, ensure_ascii=False)
    logger.info("Saved %d hERG molecules to %s", len(molecules), path)
    return str(path)


def get_chembl_herg_smiles(min_pchembl: float = 5.0) -> list[tuple[str, int]]:
    """
    Returns list of (smiles, binary_label) from ChEMBL hERG data.
    label = 1 (toxic) if pChEMBL >= min_pchembl, else 0 (safe).
    """
    import json
    path = DATA_DIR / "herg_chembl.json"
    if not path.exists():
        logger.warning("ChEMBL hERG data not found. Run fetch_and_save_herg() first.")
        return []

    with open(path, encoding="utf-8") as f:
        molecules = json.load(f)

    results = []
    for mol in molecules:
        pchembl = mol.get("pchembl_value")
        if pchembl is None:
            continue
        try:
            pv = float(pchembl)
            label = 1 if pv >= min_pchembl else 0
            results.append((mol["smiles"], label))
        except (ValueError, TypeError):
            continue

    logger.info("Loaded %d ChEMBL hERG molecules (%d toxic)", len(results), sum(1 for _, l in results if l == 1))
    return results


if __name__ == "__main__":
    path = fetch_and_save_herg(limit=200)
    if path:
        print(f"hERG data saved to: {path}")
        samples = get_chembl_herg_smiles()
        print(f"Loaded {len(samples)} molecules with pChEMBL labels")
