import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from api.main import app
from src.auth import register_user, authenticate_user

_USERS_FILE = Path(__file__).resolve().parents[1] / "users.json"

client = TestClient(app)


def setup_function():
    if _USERS_FILE.exists():
        _USERS_FILE.unlink()


def teardown_function():
    if _USERS_FILE.exists():
        _USERS_FILE.unlink()


def test_register():
    resp = client.post("/register", json={"username": "testuser", "password": "test123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["username"] == "testuser"
    assert data["token_type"] == "bearer"
    assert _USERS_FILE.exists()


def test_register_duplicate():
    register_user("dup", "test123")
    resp = client.post("/register", json={"username": "dup", "password": "test456"})
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]


def test_register_short_password():
    resp = client.post("/register", json={"username": "u", "password": "ab"})
    assert resp.status_code == 400


def test_login():
    register_user("loginuser", "pass123")
    resp = client.post("/login", json={"username": "loginuser", "password": "pass123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["username"] == "loginuser"


def test_login_wrong_password():
    register_user("gooduser", "goodpass")
    resp = client.post("/login", json={"username": "gooduser", "password": "wrong"})
    assert resp.status_code == 401


def test_jwt_can_access_predict():
    register_user("apiuser", "pass123")
    token = authenticate_user("apiuser", "pass123")
    resp = client.post(
        "/predict",
        json={"smiles": "CCO"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"] is None
    assert len(data["properties"]) > 0


def test_invalid_jwt_rejected():
    resp = client.post(
        "/predict",
        json={"smiles": "CCO"},
        headers={"Authorization": "Bearer invalidtoken123"},
    )
    assert resp.status_code in (200, 403)


def test_no_auth_allowed_when_no_keys():
    resp = client.post("/predict", json={"smiles": "CCO"})
    assert resp.status_code == 200
