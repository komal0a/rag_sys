import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

# Ensure backend package is importable when pytest runs from workspace root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
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


# Create tables for tests
models.Base.metadata.create_all(bind=engine)

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_routes_registered():
    paths = {r.path for r in app.routes}
    assert any(p.startswith("/users") for p in paths), "users routes not registered"
    assert any(p.startswith("/documents") for p in paths), "documents routes not registered"


def test_create_and_list_users():
    resp = client.post("/users/", json={"email": "a@example.com", "password": "pass"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "a@example.com"

    resp2 = client.get("/users/")
    assert resp2.status_code == 200
    assert any(u["email"] == "a@example.com" for u in resp2.json())


def test_create_user_duplicate():
    client.post("/users/", json={"email": "dup@example.com", "password": "p"})
    resp = client.post("/users/", json={"email": "dup@example.com", "password": "p"})
    assert resp.status_code == 400


def test_create_and_list_documents():
    u = client.post("/users/", json={"email": "owner@example.com", "password": "pw"}).json()
    resp = client.post("/documents/", json={"user_id": u["id"], "filename": "doc.pdf", "num_pages": 3})
    assert resp.status_code == 200
    doc = resp.json()
    assert doc["filename"] == "doc.pdf"

    resp2 = client.get("/documents/")
    assert resp2.status_code == 200
    assert any(d["filename"] == "doc.pdf" for d in resp2.json())


def test_create_document_user_not_found():
    resp = client.post("/documents/", json={"user_id": 999999, "filename": "x"})
    assert resp.status_code == 404
