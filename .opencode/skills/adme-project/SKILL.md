---
name: adme-project
description: Use when working on the ADMETox.AI drug screening platform. Covers project structure, code conventions, testing patterns, and optimization rules.
---

# ADMETox.AI Project Guidelines

## Stack
- Python 3.14 (host) / Python 3.12 (ROCm container)
- LightGBM classification/regression models (`.pkl`)
- GNN: PyTorch + DGL + GIN encoder (`.pt`)
- API: FastAPI + Pydantic v2
- UI: Streamlit
- GPU: AMD Radeon RX 6900 XT (ROCm 6.3)

## Directory Structure
```
adme_proto/
├── api/               # FastAPI endpoints (main.py, schemas.py, auth.py)
├── src/               # Core logic
│   ├── endpoints.py   # 41 endpoint definitions (10 legacy + 31 new)
│   ├── features.py    # RDKit descriptors + Morgan fingerprints (lru_cache)
│   ├── gnn_features.py# DGL graph featurizer (116 atom + 12 bond features)
│   ├── gnn.py         # GIN encoder with gradient checkpointing
│   ├── hybrid_model.py# GNN + descriptor fusion head
│   ├── predict.py     # ADMETPredictor (hybrid first, LightGBM fallback)
│   ├── train_hybrid.py# Training pipeline
│   ├── config.py      # Paths, logger, dataset metadata
│   ├── models.py      # model loading with safetensors support
│   └── usage.py       # SQLite usage logging (thread-safe, bulk insert)
├── tests/             # pytest tests
├── deploy/docker/     # Docker dev compose + ROCm
├── models/            # Trained .pkl and .pt files
└── tools/             # MIOpen warmup, SOTA benchmark
```

## Code Conventions
- **No comments** in production code (self-documenting)
- Type hints on all function signatures
- `lru_cache` for heavy computations (canonicalize_smiles, descriptors)
- Lazy model loading (scan paths in __init__, load on first use)
- Thread-safe SQLite with `threading.Lock()` + WAL mode
- `html.escape()` all user values rendered in `unsafe_allow_html=True`
- `re.sub(r'[^\w\-]', '_', ...)` for filename sanitization

## Testing
- Run: `pytest tests/ -q --tb=short -W ignore::DeprecationWarning`
- Skip GPU tests: `-k "not gpu"`
- GNN/hybrid tests auto-skip if torch/dgl absent
- **Current status**: 97 passed, 7 failed, 18 skipped
- **Failed tests** (pre-existing):
  - `test_register_short_password` (Pydantic v2 returns 422 instead of 400)
  - `test_validation_drugs_known_classes` (iteration mismatch)
  - `test_pdf_report_generates` (lang parameter conflict)
  - `test_cyp2d6_sota_threshold` (AUC 0.021 vs threshold 0.94)
  - `test_solubility_r2_threshold` (prediction out of range)
  - `test_single_prediction_latency` (38ms > 30ms threshold)
  - `test_warmup_speedup` (warmup not effective on CPU)
  - `test_throughput` (27 pred/s < 30 threshold)

## Launch & Debug
- **start.bat** — main launcher (pure ASCII, no encoding issues)
- **start_simple.bat** — simplified launcher without venv activation
- **LAUNCH.html** — user-friendly launcher with status check
- **test_predict.py** — manual prediction testing script
- **test_streamlit.py** — Streamlit server testing script
- **TEST_RESULTS.md** — comprehensive test results documentation
- **Model integrity**: `models/checksums.txt` contains SHA256 hashes for all 11 models
- **Known issue**: `start.bat` must be pure ASCII (no Russian characters) to work in cmd.exe

## Security Rules
- S1: Use safetensors (not pickle) for model serialization
- S2: No path traversal in API params
- S3: Rate limit all public endpoints
- S4: Validate file uploads (MIME, size, encoding, engine='c')
- S5: Pydantic Field(min_length=1, max_length=64, pattern=...)
- S6: html.escape() all user input in HTML context
- S8: max_chars on text inputs

## Optimization Targets
- Single predict: <50ms (current: ~26ms ✅)
- Batch predict avg: <15ms (current: ~32ms ⚠️)
- Startup: <0.3s (current: ~1.7s)
- RAM: <150 MB (current: ~200 MB)
- Warnings: <50 (current: 1 ✅)

## Key Patterns
- Predictor loads models lazily, scans `.pkl` files in `__init__`
- `predict_batch()` parallelizes feature computation via `ThreadPoolExecutor(max_workers=8)`
- Batch logging uses `log_predictions_batch(records)` single SQLite insert
- Feature computation uses `_compute_all_features_cached` + `.copy()` for cache safety
- Validation drugs accessed through `VALIDATION_DRUGS` dict in `config.py`

## Model Files
Models are stored in `models/` directory and loaded on demand:
- `{key}_model.pkl` — LightGBM models
- `hybrid_model.pt` — GNN+LightGBM hybrid (if trained)
- `checksums.txt` — SHA256 hashes for all models (integrity verification)
- Check `MODELS_DIR` in `src/config.py` for the exact path
- **Model loading**: Uses `joblib.load()` with SHA256 integrity check
- **Lazy loading**: Models loaded on first use, not at startup
- **Current models**: 11 total (solubility, caco2, herg, lipophilicity, pgp, cyp3a4, cyp2d6, ames, bioavailability, ppbr, herg_expanded)

## Security & Privacy
- **No secrets in git**: All sensitive data in `D:\AI\biotech\secrets\` (gitignored)
- **GitHub token revoked**: Old token has been revoked, new one stored securely
- **No PII in code**: Removed personal GitHub username, replaced with `Recconnect` org
- **No absolute paths**: Replaced local paths with relative paths in docs
- **Client engagement**: Separate project at `D:\AI\biotech\client_engagement\` (NOT in repo)

## Git Workflow
- **Remote**: `https://github.com/Recconnect/ADME-Tox-Predictor.git`
- **Branch**: `master`
- **Push protection**: GitHub blocks pushes with secrets (token, API keys)
- **Pre-commit checks**:
  - `git diff --cached | grep -i "token\|password\|secret"` — no secrets
  - `git diff --cached | grep "D:\\AI\\biotech"` — no absolute paths
  - `git ls-files | grep client_engagement` — no client data

## Common Issues & Fixes
1. **start.bat doesn't work**: Use `start_simple.bat` instead (encoding issue)
2. **"No checksums file found" warning**: Fixed by adding `models/checksums.txt`
3. **Port 8501 blocked**: Check firewall, or use `--server.port=8502`
4. **Streamlit not responding**: Run `test_streamlit.py` to diagnose
5. **Model integrity failure**: Regenerate `checksums.txt` with `Get-FileHash`

## Recent Improvements (2026-07-06)
- **Phase A implementation**: GNN + LightGBM hybrid model architecture
- **Security hardening**: XSS protection, input validation, rate limiting
- **Performance optimization**: ThreadPoolExecutor for batch predictions
- **Model integrity**: SHA256 checksums for all 11 models
- **Testing infrastructure**: Added test scripts and documentation
- **Git cleanup**: Removed PII, absolute paths, secrets exposure
- **Fixed**: 10x "No checksums file found" warnings at startup
- **Added**: `start_simple.bat`, `LAUNCH.html`, `TEST_RESULTS.md`

## File Locations
- **Main app**: `D:\AI\biotech\adme_proto\app.py`
- **API**: `D:\AI\biotech\adme_proto\api\main.py`
- **Models**: `D:\AI\biotech\adme_proto\models\`
- **Tests**: `D:\AI\biotech\adme_proto\tests\`
- **Secrets**: `D:\AI\biotech\secrets\` (gitignored, NOT in repo)
- **Client engagement**: `D:\AI\biotech\client_engagement\` (separate project)
