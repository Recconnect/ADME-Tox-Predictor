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
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.predict import ADMETPredictor
from src.features import canonicalize_smiles
from src.config import VALIDATION_DRUGS, MODELS_DIR, logger
from src.auth import register_user, authenticate_user, verify_token as verify_jwt_token
from src.usage import log_prediction, get_stats
from api.schemas import (
    PredictRequest, PredictResponse, PropertyResult,
    BatchPredictRequest, BatchPredictResponse,
    HealthResponse, RegisterRequest, LoginRequest, AuthResponse,
    UsageStatsResponse,
)

_START_TIME = time.time()
_LANDING_DIR = Path(__file__).resolve().parents[1] / "landing"

limiter = Limiter(key_func=get_remote_address)

REQUEST_COUNT = Counter("admetox_requests_total", "Total requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("admetox_request_latency_seconds", "Request latency", ["endpoint"])

API_KEYS = set()
_api_key_env = os.environ.get("ADMETOX_API_KEYS", "")
if _api_key_env:
    API_KEYS.update(k.strip() for k in _api_key_env.split(",") if k.strip())

security = HTTPBearer(auto_error=False)


def verify_api_key(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    if credentials is None:
        if API_KEYS:
            raise HTTPException(403, "Missing authorization token")
        return
    token = credentials.credentials
    if token in API_KEYS:
        return
    payload = verify_jwt_token(token)
    if payload is not None:
        request.state.user = payload.get("sub")
        request.state.role = payload.get("role", "user")
        return
    if API_KEYS:
        raise HTTPException(403, "Invalid or missing API key. Set ADMETOX_API_KEYS env var.")


app = FastAPI(
    title="ADMETox.AI API",
    description="AI-powered ADME/Tox prediction for drug discovery. "
                "Predict solubility, Caco-2 permeability, hERG toxicity, lipophilicity, and P-gp from SMILES.",
    version="2.0.0",
    contact={"name": "ADMETox.AI", "url": "https://admetox.ai"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    endpoint = request.url.path
    REQUEST_COUNT.labels(method=request.method, endpoint=endpoint).inc()
    response = await call_next(request)
    elapsed = time.time() - start
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(elapsed)
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
        ("Lipophilicity (logD)", None),
        ("P-gp Inhibition", None),
        ("P-gp Class", None),
        ("CYP3A4 Inhibition", None),
        ("CYP3A4 Class", None),
        ("CYP2D6 Inhibition", None),
        ("CYP2D6 Class", None),
        ("Ames Mutagenicity", None),
        ("Ames Class", None),
        ("Bioavailability", None),
        ("Bioavailability Class", None),
        ("PPB (plasma binding)", None),
        ("PPB Class", None),
    ]
    for name, unit in prop_names:
        if name in result:
            props.append(PropertyResult(name=name, value=result[name], unit=unit))

    desc_keys = [k for k in result.keys() if k not in
                 [p[0] for p in prop_names] + ["error", "SMILES"]]
    for k in desc_keys:
        props.append(PropertyResult(name=k, value=result[k]))
    return props


@app.get("/", include_in_schema=False)
def serve_landing():
    index = _LANDING_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return JSONResponse({"status": "ADMETox.AI API is running", "docs": "/docs"})


if _LANDING_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_LANDING_DIR)), name="landing")


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    n_loaded = len(predictor.models)
    import psutil
    mem = psutil.Process().memory_info().rss / 1024 / 1024
    model_files = {k: str(MODELS_DIR / f"{k}_model.pkl") for k in predictor.models}
    return HealthResponse(
        status="ready" if predictor.is_ready else "degraded",
        models_loaded=n_loaded,
        models_expected=10,
        version="2.0",
        uptime_seconds=int(time.time() - _START_TIME),
        memory_mb=round(mem, 1),
        model_files=model_files,
    )


@app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
@limiter.limit("60/minute")
def predict_single(request: Request, req: PredictRequest, _: None = Depends(verify_api_key)):
    t0 = time.time()
    result = _do_predict(req.smiles)
    latency = (time.time() - t0) * 1000
    username = getattr(request.state, "user", None)
    log_prediction(
        username=username,
        smiles=req.smiles,
        canonical_smiles=result.canonical_smiles,
        properties={p.name: p.value for p in result.properties} if result.properties else None,
        error=result.error,
        latency_ms=latency,
    )
    return result


@app.post("/batch", response_model=BatchPredictResponse, tags=["Prediction"])
@limiter.limit("10/minute")
def predict_batch(request: Request, req: BatchPredictRequest, _: None = Depends(verify_api_key)):
    n = len(req.smiles)
    if n > 10000:
        raise HTTPException(400, f"Batch size {n} exceeds limit 10000")

    results = []
    failed = 0
    username = getattr(request.state, "user", None)
    for smi in req.smiles:
        t0 = time.time()
        r = _do_predict(smi)
        latency = (time.time() - t0) * 1000
        log_prediction(
            username=username,
            smiles=smi,
            canonical_smiles=r.canonical_smiles,
            properties={p.name: p.value for p in r.properties} if r.properties else None,
            error=r.error,
            latency_ms=latency,
        )
        results.append(r)
        if r.error:
            failed += 1

    return BatchPredictResponse(results=results, total=n, failed=failed)


@app.get("/metrics", tags=["System"])
def get_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/register", response_model=AuthResponse, tags=["Auth"])
@limiter.limit("5/minute")
def register(request: Request, req: RegisterRequest):
    err = register_user(req.username, req.password)
    if err:
        raise HTTPException(400, err)
    token = authenticate_user(req.username, req.password)
    if not token:
        raise HTTPException(500, "Registration succeeded but login failed")
    return AuthResponse(access_token=token, username=req.username)


@app.post("/login", response_model=AuthResponse, tags=["Auth"])
@limiter.limit("20/minute")
def login(request: Request, req: LoginRequest):
    token = authenticate_user(req.username, req.password)
    if not token:
        raise HTTPException(401, "Invalid username or password")
    return AuthResponse(access_token=token, username=req.username)


@app.get("/admin/usage", response_model=UsageStatsResponse, tags=["Admin"])
def admin_usage(days: int = 7):
    stats = get_stats(days)
    return UsageStatsResponse(**stats)


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
