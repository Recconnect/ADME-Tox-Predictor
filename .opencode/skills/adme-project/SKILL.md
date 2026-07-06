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
- Pre-existing failures (5): model regression thresholds, PDF lang, warmup speed

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
- Check `MODELS_DIR` in `src/config.py` for the exact path
