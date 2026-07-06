# ADMETox.AI — AI Drug Screener

AI-powered ADME/Tox prediction platform for drug discovery. Predict 11 key properties from SMILES strings in seconds.

## Features

- **11 ADME/Tox models**: Solubility, Caco-2, hERG, Lipophilicity, P-gp, CYP3A4, CYP2D6, Ames, Bioavailability, PPB, and more
- **FastAPI REST API** with JWT authentication and rate limiting
- **Streamlit UI** with bilingual support (English/Russian)
- **PDF reports** with professional formatting
- **Radar charts** for ADME profile visualization
- **Security-hardened**: 14 security fixes applied (JWT, CORS, XSS protection, etc.)
- **Docker-ready** with nginx + certbot for production deployment
- **Client engagement system** for automated outreach (separate project)

## Quick Start

### Local Development

```bash
# Windows
.\venv\Scripts\activate
streamlit run app.py

# Or use the launcher
start.bat
```

Open http://localhost:8501

### Docker (Production)

```bash
# Clone
git clone https://github.com/Recconnect/ADME-Tox-Predictor.git
cd ADME-Tox-Predictor

# Setup environment
cp .env.example .env
# Edit .env: set ADMETOX_JWT_SECRET (openssl rand -hex 32)

# Build and run
docker compose up -d --build
```

Access:
- Landing: http://localhost
- UI: http://localhost/ui/
- API docs: http://localhost/docs

## Models

| Model | Task | Dataset | Test Metric |
|-------|------|---------|-------------|
| Solubility | Regression | AqSolDB (9,982) | R² = 0.826 |
| Caco-2 | Classification | Wang et al. (910) | Acc = 83.0%, AUC = 0.884 |
| hERG | Classification | TDC (655) | Acc = 80.3%, AUC = 0.873 |
| Lipophilicity | Regression | AqSolDB (9,982) | R² = 0.815 |
| P-gp | Classification | TDC (1,117) | Acc = 85.2%, AUC = 0.912 |
| CYP3A4 | Classification | TDC (12,286) | Acc = 87.4%, AUC = 0.934 |
| CYP2D6 | Classification | TDC (13,130) | Acc = 89.1%, AUC = 0.945 |
| Ames | Classification | TDC (7,831) | Acc = 86.3%, AUC = 0.921 |
| Bioavailability | Classification | TDC (763) | Acc = 78.5%, AUC = 0.856 |
| PPB | Regression | TDC (1,614) | R² = 0.742 |
| hERG (expanded) | Classification | TDC (9,505) | Acc = 84.7%, AUC = 0.918 |

All models exceed target metrics (R² > 0.6, Acc > 75%, AUC > 0.7).

## Usage

### Web Interface (Streamlit)

1. **Single Prediction** — enter SMILES (e.g., `CCO`), click Predict
2. **Batch Prediction** — enter multiple SMILES (one per line) or upload CSV
3. **Validation** — test on 10 known drugs (aspirin, ibuprofen, etc.)

### Python API

```python
from src.predict import ADMETPredictor

predictor = ADMETPredictor()
result = predictor.predict_single("CCO")
print(result["Solubility (logS)"])      # 0.938
print(result["Caco-2 Class"])           # High permeability
print(result["hERG Class"])             # Safe (low risk)
```

### REST API

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"smiles": "CCO"}'
```

## Architecture

```
adme_proto/
├── src/                  # Core: features, models, predict, config, i18n, pdf, radar
├── api/                  # FastAPI REST API (main.py, schemas.py, auth.py)
├── app.py                # Streamlit UI
├── models/               # 11 .pkl models (embedded in Docker image)
├── data/                 # Raw .tab datasets
├── landing/              # Static landing page
├── deploy/
│   ├── nginx/            # Dockerfile + nginx config for Docker
│   ├── nginx.conf        # Production nginx (bare-metal)
│   ├── systemd/          # systemd unit files
│   └── Makefile          # deploy/update/restart commands
├── Dockerfile            # Multi-stage: base → api / ui
├── docker-compose.yml    # 3 services: nginx + api + ui (+ certbot for SSL)
├── .env.example          # Environment variables template
└── start.bat             # Windows launcher
```

## Security

Production-ready with 14 security fixes:

- **C-1**: JWT secret generation (no hardcoded fallback)
- **C-2**: CORS whitelist (ADMETOX_CORS_ORIGINS)
- **C-3**: Admin endpoint authentication
- **H-1**: Model file integrity verification (SHA-256)
- **H-2**: XSS protection (HTML escaping)
- **H-3**: Password policy (min 8 chars)
- **H-4**: File permissions (0o600 on sensitive files)
- **H-5**: Metrics endpoint authentication
- **M-1**: Reload mode controlled by environment variable
- **M-3**: Login rate limiting (5/min)
- **M-5**: SMILES truncation in error messages
- **M-6**: Input validation (max_length=10000)
- **M-7**: CSV upload validation

## Testing

```bash
# Run all tests (69 tests)
python -m pytest tests/ -v

# Test specific module
python -m pytest tests/test_predict.py -v
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ADMETOX_JWT_SECRET` | ✅ | (generated) | JWT signing secret |
| `ADMETOX_API_KEYS` | ❌ | — | Comma-separated API keys |
| `ADMETOX_CORS_ORIGINS` | ❌ | `https://admetox.ai` | Allowed CORS origins |
| `DOMAIN` | for SSL | — | Domain for Let's Encrypt |
| `SSL_EMAIL` | for SSL | — | Email for Let's Encrypt |

## Client Engagement (Separate Project)

Automated outreach system for product promotion and investor relations:

**Location:** `D:\AI\biotech\client_engagement\`

**7 specialized agents:**
1. GitHub Agent — auto-release, changelog, issue responses
2. Content Agent — article generation via LLM
3. Investor Agent — email outreach to 66 biotech investors
4. Feedback Agent — GitHub feedback collection
5. Conference Agent — conference tracking
6. Social Media Agent — LinkedIn, Twitter, Medium posts
7. Metrics Agent — weekly reports

See `client_engagement/README.md` for details.

## Data Sources

- **AqSolDB** — water solubility (9,982 molecules) — Harvard Dataverse ID: 4259610
- **Caco-2** — permeability (910 molecules) — Harvard Dataverse ID: 4259569
- **hERG** — toxicity (655 molecules) — Harvard Dataverse ID: 4259588
- **TDC** — Therapeutics Data Commons (multiple datasets)

## Performance

| Metric | Value |
|--------|-------|
| Single predict | ~26ms (after warmup) |
| Batch predict | ~32ms/mol |
| Startup time | 1.74s (import) + 0.00s (lazy load) |
| RAM usage | ~200 MB |

## Domain

Recommended: **admetox.ai** (available, verified via whois)

## License

Internal use only. Not for distribution.

## Notes

- Caco-2 dataset binarized at logPapp > -5.5 (high permeability)
- Production use requires fine-tuning on corporate data and ICH M7/FDA validation
- Open-source models do NOT replace experimental validation
