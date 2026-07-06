from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    smiles: str = Field(max_length=10000)


class BatchPredictRequest(BaseModel):
    smiles: list[str] = Field(max_length=10000, description="List of SMILES strings (max 10000)")


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


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str = "user"


class UsageStatsResponse(BaseModel):
    total_predictions: int
    predictions_7d: int
    errors: int
    unique_users: int
    unique_smiles: int
    avg_latency_ms: float
    top_users: list[dict]
    hourly_7d: list[dict]
