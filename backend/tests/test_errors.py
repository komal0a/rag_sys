import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app
from app import models
from app.deps import get_db
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


def register_and_token(email="err@example.com", password="pw12345"):
    client.post("/auth/register", json={"email": email, "password": password})
    r = client.post("/auth/login", json={"email": email, "password": password})
    return r.json()["access_token"]


def test_passwords_are_hashed():
    token = register_and_token("hash@example.com", "secretpw")
    # inspect DB
    db = TestingSessionLocal()
    u = db.query(models.User).filter(models.User.email == "hash@example.com").first()
    assert u is not None
    assert u.hashed_password != "secretpw"


def test_upload_invalid_file_rejected():
    token = register_and_token("up@example.com", "pw12345")
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("test.txt", b"not a pdf", "text/plain")}
    r = client.post("/documents/upload", files=files, headers=headers)
    assert r.status_code == 400


def test_upload_oversize_rejected():
    token = register_and_token("big@example.com", "pw12345")
    headers = {"Authorization": f"Bearer {token}"}
    # temporarily set max upload to 0 MB
    old = config.settings.MAX_UPLOAD_SIZE_MB
    config.settings.MAX_UPLOAD_SIZE_MB = 0
    try:
        files = {"file": ("f.pdf", b"%PDF-1.4 small", "application/pdf")}
        r = client.post("/documents/upload", files=files, headers=headers)
        assert r.status_code == 400
    finally:
        config.settings.MAX_UPLOAD_SIZE_MB = old


def test_llm_failure_returns_502():
    token = register_and_token("llm@example.com", "pw12345")
    headers = {"Authorization": f"Bearer {token}"}
    # create a document and chunk
    db = TestingSessionLocal()
    user = db.query(models.User).filter(models.User.email == "llm@example.com").first()
    doc = models.Document(user_id=user.id, filename="doc.pdf", status="uploaded")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    # add a chunk
    ch = models.DocumentChunk(document_id=doc.id, chunk_index=0, content="foo", embedding=[0.1]*8)
    db.add(ch)
    db.commit()

    # monkeypatch provider used by chat endpoint to raise, restore afterwards
    import importlib
    import app.api.chat as chat_mod

    class BadProvider:
        def generate(self, prompt):
            raise RuntimeError("boom")

    old = getattr(chat_mod, "get_provider")
    try:
        chat_mod.get_provider = lambda: BadProvider()
        r = client.post("/chat", json={"query": "hi", "document_id": doc.id}, headers=headers)
        assert r.status_code == 502
    finally:
        chat_mod.get_provider = old


def test_embedding_failure_returns_500():
    token = register_and_token("emb@example.com", "pw12345")
    headers = {"Authorization": f"Bearer {token}"}
    # monkeypatch Retriever.embed_query to raise and restore afterwards
    from app.services.retrieval import Retriever

    old_embed = Retriever.embed_query
    try:
        def _bad(self, q):
            raise RuntimeError("embed fail")

        Retriever.embed_query = _bad
        # TestClient by default re-raises server exceptions; use a client that doesn't raise
        from fastapi.testclient import TestClient as TC
        c2 = TC(app, raise_server_exceptions=False)
        r = c2.post("/documents/search", json={"query": "x"}, headers=headers)
        assert r.status_code == 500
    finally:
        Retriever.embed_query = old_embed
