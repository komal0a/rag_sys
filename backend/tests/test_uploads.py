import tempfile
import os
from fastapi.testclient import TestClient
from pathlib import Path
import sys
from pathlib import Path

# Ensure backend package importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app
from app import models
from app.deps import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core import config

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app = create_app()

models.Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def register_and_token(email="u@example.com", password="secret"):
    client.post("/auth/register", json={"email": email, "password": password})
    r = client.post("/auth/login", json={"email": email, "password": password})
    return r.json()["access_token"]


def test_upload_success_and_delete():
    token = register_and_token("up@example.com", "pw12345")
    headers = {"Authorization": f"Bearer {token}"}
    with tempfile.TemporaryDirectory() as d:
        # point storage to temp dir
        config.settings.UPLOAD_DIR = d
        config.settings.MAX_UPLOAD_SIZE_MB = 1
        pdf_bytes = b"%PDF-1.4\n%EOF\n"
        files = {"file": ("test.pdf", pdf_bytes, "application/pdf")}
        resp = client.post("/documents/upload", files=files, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        doc_id = data["id"]
        # file exists
        docs = client.get("/documents/", headers=headers).json()
        assert any(d["id"] == doc_id for d in docs)

        # delete
        r = client.delete(f"/documents/{doc_id}", headers=headers)
        assert r.status_code == 200
        assert r.json()["status"] == "deleted"


def test_upload_invalid_type():
    token = register_and_token("inv@example.com", "pw12345")
    headers = {"Authorization": f"Bearer {token}"}
    with tempfile.TemporaryDirectory() as d:
        config.settings.UPLOAD_DIR = d
        files = {"file": ("bad.txt", b"hello", "text/plain")}
        resp = client.post("/documents/upload", files=files, headers=headers)
        assert resp.status_code == 400


def test_upload_requires_auth():
    with tempfile.TemporaryDirectory() as d:
        config.settings.UPLOAD_DIR = d
        files = {"file": ("test.pdf", b"%PDF-1.4\n%EOF\n", "application/pdf")}
        resp = client.post("/documents/upload", files=files)
        assert resp.status_code == 401


def test_upload_size_limit():
    token = register_and_token("size@example.com", "pw12345")
    headers = {"Authorization": f"Bearer {token}"}
    with tempfile.TemporaryDirectory() as d:
        config.settings.UPLOAD_DIR = d
        # set size limit to 0 MB
        config.settings.MAX_UPLOAD_SIZE_MB = 0
        files = {"file": ("test.pdf", b"%PDF-1.4\n%EOF\n", "application/pdf")}
        resp = client.post("/documents/upload", files=files, headers=headers)
        assert resp.status_code == 400
