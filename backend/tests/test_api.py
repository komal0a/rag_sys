import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

# Ensure backend package is importable when pytest runs from workspace root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app
from app import models
from app.deps import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app = create_app()

# Create tables for tests
models.Base.metadata.create_all(bind=engine)

# Override the dependency on this app instance
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_routes_registered():
    paths = {r.path for r in app.routes}
    assert any(p.startswith("/auth") for p in paths), "auth routes not registered"
    assert any(p.startswith("/documents") for p in paths), "documents routes not registered"


def test_register_and_login_flow():
    # register
    resp = client.post("/auth/register", json={"email": "a@example.com", "password": "pass123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "a@example.com"

    # login
    resp2 = client.post("/auth/login", json={"email": "a@example.com", "password": "pass123"})
    assert resp2.status_code == 200
    token = resp2.json().get("access_token")
    assert token

    # protected endpoint requires token
    r = client.get("/documents/")
    assert r.status_code == 401


def test_register_duplicate():
    client.post("/auth/register", json={"email": "dup@example.com", "password": "pword"})
    resp = client.post("/auth/register", json={"email": "dup@example.com", "password": "pword"})
    assert resp.status_code == 400


def test_create_and_list_documents():
    client.post("/auth/register", json={"email": "owner@example.com", "password": "pw12345"})
    login = client.post("/auth/login", json={"email": "owner@example.com", "password": "pw12345"}).json()
    token = login["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/documents/", json={"filename": "doc.pdf", "num_pages": 3}, headers=headers)
    assert resp.status_code == 200
    doc = resp.json()
    assert doc["filename"] == "doc.pdf"

    resp2 = client.get("/documents/", headers=headers)
    assert resp2.status_code == 200
    assert any(d["filename"] == "doc.pdf" for d in resp2.json())


def test_login_fail_and_jwt_checks():
    # bad login
    resp = client.post("/auth/login", json={"email": "nope@example.com", "password": "x"})
    assert resp.status_code == 401

    # invalid token access
    headers = {"Authorization": "Bearer invalid.token.here"}
    r = client.get("/documents/", headers=headers)
    assert r.status_code == 401
