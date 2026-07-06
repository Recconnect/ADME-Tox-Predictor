import sqlite3
import time
import json
from pathlib import Path
from datetime import datetime

_DB_PATH = Path(__file__).resolve().parents[1] / "usage.db"


def _get_conn():
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            smiles TEXT NOT NULL,
            canonical_smiles TEXT,
            timestamp REAL NOT NULL,
            properties TEXT,
            error TEXT,
            latency_ms REAL
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_predictions_username
        ON predictions(username)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_predictions_timestamp
        ON predictions(timestamp)
    """)
    conn.commit()
    return conn


def log_prediction(
    username: str | None,
    smiles: str,
    canonical_smiles: str | None,
    properties: dict | None,
    error: str | None,
    latency_ms: float,
):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO predictions (username, smiles, canonical_smiles, timestamp, properties, error, latency_ms) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            username,
            smiles,
            canonical_smiles,
            time.time(),
            json.dumps(properties, ensure_ascii=False) if properties else None,
            error,
            latency_ms,
        ),
    )
    conn.commit()
    conn.close()


def get_stats(days: int = 7) -> dict:
    conn = _get_conn()
    cutoff = time.time() - days * 86400
    total = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    total_7d = conn.execute("SELECT COUNT(*) FROM predictions WHERE timestamp >= ?", (cutoff,)).fetchone()[0]
    errors = conn.execute("SELECT COUNT(*) FROM predictions WHERE error IS NOT NULL").fetchone()[0]
    unique_users = conn.execute("SELECT COUNT(DISTINCT username) FROM predictions WHERE username IS NOT NULL").fetchone()[0]
    unique_smiles = conn.execute("SELECT COUNT(DISTINCT smiles) FROM predictions").fetchone()[0]
    avg_latency = conn.execute("SELECT AVG(latency_ms) FROM predictions WHERE latency_ms IS NOT NULL").fetchone()[0]

    top_users = conn.execute(
        "SELECT username, COUNT(*) as cnt FROM predictions WHERE username IS NOT NULL "
        "GROUP BY username ORDER BY cnt DESC LIMIT 10"
    ).fetchall()

    hourly = conn.execute(
        "SELECT strftime('%Y-%m-%d %H:00', datetime(timestamp, 'unixepoch')) as hour, COUNT(*) as cnt "
        "FROM predictions WHERE timestamp >= ? GROUP BY hour ORDER BY hour",
        (cutoff,),
    ).fetchall()

    conn.close()

    return {
        "total_predictions": total,
        "predictions_7d": total_7d,
        "errors": errors,
        "unique_users": unique_users,
        "unique_smiles": unique_smiles,
        "avg_latency_ms": round(avg_latency, 2) if avg_latency else 0,
        "top_users": [{"username": r["username"], "count": r["cnt"]} for r in top_users],
        "hourly_7d": [{"hour": r["hour"], "count": r["cnt"]} for r in hourly],
    }
