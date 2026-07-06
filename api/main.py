"""
FastAPI REST API for ADMETox.AI

Запуск:
    uvicorn api.main:app --reload --port 8000

Документация:
    http://localhost:8000/docs
    http://localhost:8000/redoc
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.predict import ADMETPredictor
from src.features import canonicalize_smiles, compute_rdkit_descriptors
from src.config import VALIDATION_DRUGS, MODELS_DIR
from api.schemas import (
    PredictRequest, PredictResponse, PropertyResult,
    BatchPredictRequest, BatchPredictResponse,
    HealthResponse,
)

_START_TIME = time.time()

app = FastAPI(
    title="ADMETox.AI API",
    description="AI-powered ADME/Tox prediction for drug discovery. "
                "Predict solubility, Caco-2 permeability, and hERG toxicity from SMILES.",
    version="2.0.0",
    contact={"name": "ADMETox.AI", "url": "https://admetox.ai"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    response.headers["X-Process-Time"] = str(round(elapsed, 4))
    return response


predictor = ADMETPredictor()


def _result_to_properties(result: dict) -> list[PropertyResult]:
    props = []
    prop_names = [
        ("Solubility (logS)", None),
        ("SolubilityClass", None),
        ("Caco-2 Permeability", None),
        ("Caco-2 Class", None),
        ("hERG Toxicity Risk", None),
        ("hERG Class", None),
    ]
    for name, unit in prop_names:
        if name in result:
            props.append(PropertyResult(name=name, value=result[name], unit=unit))

    desc_keys = [k for k in result.keys() if k not in
                 [p[0] for p in prop_names] + ["error", "SMILES"]]
    for k in desc_keys:
        props.append(PropertyResult(name=k, value=result[k]))
    return props


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    n_loaded = len(predictor.models)
    import psutil
    mem = psutil.Process().memory_info().rss / 1024 / 1024
    model_files = {k: str(MODELS_DIR / f"{k}_model.pkl") for k in predictor.models}
    return HealthResponse(
        status="ready" if predictor.is_ready else "degraded",
        models_loaded=n_loaded,
        models_expected=5,
        version="2.0",
        uptime_seconds=int(time.time() - _START_TIME),
        memory_mb=round(mem, 1),
        model_files=model_files,
    )


@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
def predict_single(req: PredictRequest):
    return _do_predict(req.smiles)


@app.post("/batch", response_model=BatchPredictResponse, tags=["Prediction"])
def predict_batch(req: BatchPredictRequest):
    n = len(req.smiles)
    if n > 10000:
        raise HTTPException(400, f"Batch size {n} exceeds limit 10000")

    results = []
    failed = 0
    for smi in req.smiles:
        r = _do_predict(smi)
        results.append(r)
        if r.error:
            failed += 1

    return BatchPredictResponse(results=results, total=n, failed=failed)


@app.get("/validate", response_model=list[PredictResponse], tags=["Prediction"])
def predict_validation():
    results = []
    for name, smi in VALIDATION_DRUGS.items():
        r = _do_predict(smi)
        if not r.error:
            r.smiles = name
        results.append(r)
    return results


def _do_predict(smiles: str) -> PredictResponse:
    if not smiles or not smiles.strip():
        return PredictResponse(smiles=smiles, error="Empty SMILES string")

    canon = canonicalize_smiles(smiles)
    if canon is None:
        return PredictResponse(smiles=smiles, error=f"Invalid SMILES: {smiles}")

    result = predictor.predict_single(smiles)

    if "error" in result:
        return PredictResponse(
            smiles=smiles, canonical_smiles=canon,
            error=result["error"],
        )

    props = _result_to_properties(result)
    return PredictResponse(
        smiles=smiles,
        canonical_smiles=canon,
        properties=props,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
