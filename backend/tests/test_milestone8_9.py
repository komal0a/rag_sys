import sys
from pathlib import Path
import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app
from app import models
from app.deps import get_db
from app.services.embeddings import FakeEmbeddingProvider

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


def register_and_token(email="chat@example.com", password="pw12345"):
    client.post("/auth/register", json={"email": email, "password": password})
    r = client.post("/auth/login", json={"email": email, "password": password})
    return r.json()["access_token"]


def test_chat_answers_and_conversation_persistence():
    token = register_and_token()
    headers = {"Authorization": f"Bearer {token}"}

    # create document and chunks directly
    db = TestingSessionLocal()
    user = db.query(models.User).filter(models.User.email == "chat@example.com").first()
    doc = models.Document(user_id=user.id, filename="doc.pdf", status="uploaded")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    # prepare chunks
    p = FakeEmbeddingProvider(dim=8)
    emb = p.embed_texts(["auth uses JWT"]) [0]
    ch = models.DocumentChunk(document_id=doc.id, chunk_index=0, content="The app uses JWT tokens.", embedding=emb)
    db.add(ch)
    db.commit()

    # call chat
    r = client.post("/chat", json={"query": "What authentication mechanism does the application use?", "top_k": 5, "document_id": doc.id}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert len(data.get("sources", [])) >= 1

    # conversation created
    conv_id = data.get("conversation_id")
    assert conv_id
    # fetch conversation
    rc = client.get(f"/conversations/{conv_id}", headers=headers)
    assert rc.status_code == 200
    body = rc.json()
    assert any(m["sender"] == "assistant" for m in body["messages"]) or any("assistant" in m["sender"] for m in body["messages"])


def test_chat_auth_enforced():
    r = client.post("/chat", json={"query": "hi"})
    assert r.status_code == 401
