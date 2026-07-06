FROM python:3.12-slim AS base

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# System deps for RDKit compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential g++ \
    libxrender-dev libxext-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -r requirements.txt

COPY src/ src/
COPY api/ api/
COPY models/ models/
COPY data/ data/

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "from urllib.request import urlopen; exit(0 if urlopen('http://localhost:8501').status == 200 else 1)"

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# ── FastAPI stage ────────────────────────────────────────────
FROM base AS api

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "from urllib.request import urlopen; exit(0 if urlopen('http://localhost:8000/health').status == 200 else 1)"

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Streamlit UI stage ───────────────────────────────────────
FROM base AS ui

COPY app.py .
COPY .streamlit/ .streamlit/
COPY landing/ landing/

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "from urllib.request import urlopen; exit(0 if urlopen('http://localhost:8501').status == 200 else 1)"

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
