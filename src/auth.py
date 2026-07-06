import json
import os
import time
from pathlib import Path
from dataclasses import dataclass

import jwt
import bcrypt

JWT_SECRET = os.environ.get("ADMETOX_JWT_SECRET", "admetox-dev-secret-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

_USERS_FILE = Path(__file__).resolve().parents[1] / "users.json"


@dataclass
class User:
    username: str
    password_hash: str
    created_at: float
    role: str = "user"


def _load_users() -> dict[str, User]:
    if not _USERS_FILE.exists():
        return {}
    try:
        with open(_USERS_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return {
            k: User(**v) for k, v in raw.items()
        }
    except (json.JSONDecodeError, KeyError, TypeError):
        return {}


def _save_users(users: dict[str, User]):
    _USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    raw = {
        k: {"username": v.username, "password_hash": v.password_hash,
            "created_at": v.created_at, "role": v.role}
        for k, v in users.items()
    }
    with open(_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)


def register_user(username: str, password: str) -> str | None:
    users = _load_users()
    if username in users:
        return "Username already exists"
    if len(password) < 6:
        return "Password must be at least 6 characters"
    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users[username] = User(
        username=username,
        password_hash=pw_hash,
        created_at=time.time(),
    )
    _save_users(users)
    return None


def authenticate_user(username: str, password: str) -> str | None:
    users = _load_users()
    user = users.get(username)
    if user is None:
        return None
    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return None
    return _create_token(username, user.role)


def _create_token(username: str, role: str = "user") -> str:
    payload = {
        "sub": username,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXPIRY_HOURS * 3600,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
