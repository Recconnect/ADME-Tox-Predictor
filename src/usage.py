import sqlite3
import time
import json
import os
import stat
import threading
import numpy as np
from pathlib import Path
from datetime import datetime

_lock = threading.Lock()

_DB_PATH = Path(__file__).resolve().parents[1] / "usage.db"


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return super().default(obj)


def _set_private_perms(path: Path):
    try:
        current = stat.S_IMODE(os.stat(path).st_mode)
        private = stat.S_IRUSR | stat.S_IWUSR
        if current & 0o077 != 0:
            os.chmod(path, private)
    except OSError:
        pass


def _get_conn():
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _set_private_perms(_DB_PATH)
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
    with _lock:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO predictions (username, smiles, canonical_smiles, timestamp, properties, error, latency_ms) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                username,
                smiles,
                canonical_smiles,
                time.time(),
                json.dumps(properties, ensure_ascii=False, cls=NumpyEncoder) if properties else None,
                error,
                latency_ms,
            ),
        )
        conn.commit()
        conn.close()


def log_predictions_batch(records: list[dict]) -> None:
    if not records:
        return
    with _lock:
        conn = _get_conn()
        now = time.time()
        rows = []
        for r in records:
            rows.append((
                r.get("username"),
                r["smiles"],
                r.get("canonical_smiles"),
                now,
                json.dumps(r.get("properties"), ensure_ascii=False, cls=NumpyEncoder) if r.get("properties") else None,
                r.get("error"),
                r.get("latency_ms"),
            ))
        conn.executemany(
            "INSERT INTO predictions (username, smiles, canonical_smiles, timestamp, properties, error, latency_ms) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
        conn.close()


def get_stats(days: int = 7) -> dict:
    conn = _get_conn()
    cutoff = time.time() - days * 86400
    row = conn.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN timestamp >= ? THEN 1 ELSE 0 END) AS total_7d,
            SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END) AS errors,
            COUNT(DISTINCT CASE WHEN username IS NOT NULL THEN username END) AS unique_users,
            COUNT(DISTINCT smiles) AS unique_smiles,
            AVG(CASE WHEN latency_ms IS NOT NULL THEN latency_ms END) AS avg_latency
        FROM predictions
    """, (cutoff,)).fetchone()
    total = row["total"]
    total_7d = row["total_7d"]
    errors = row["errors"]
    unique_users = row["unique_users"]
    unique_smiles = row["unique_smiles"]
    avg_latency = row["avg_latency"]

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
