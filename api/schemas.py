from pydantic import BaseModel


class PredictRequest(BaseModel):
    smiles: str


class BatchPredictRequest(BaseModel):
    smiles: list[str]


class PropertyResult(BaseModel):
    name: str
    value: float | str
    unit: str | None = None


class PredictResponse(BaseModel):
    smiles: str
    canonical_smiles: str | None = None
    error: str | None = None
    properties: list[PropertyResult] = []


class BatchPredictResponse(BaseModel):
    results: list[PredictResponse]
    total: int
    failed: int


class HealthResponse(BaseModel):
    status: str
    models_loaded: int
    models_expected: int
    version: str = "2.0"
    uptime_seconds: int | None = None
    memory_mb: float | None = None
    model_files: dict[str, str] | None = None
