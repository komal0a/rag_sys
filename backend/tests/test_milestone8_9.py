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


def test_chat_limits_llm_context_but_returns_complete_sources(monkeypatch):
    token = register_and_token("chat-context@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    long_content = ("x" * 1500) + "THIS_MUST_NOT_REACH_THE_PROMPT" + ("y" * 470)
    captured = {}

    def fake_retrieve(self, query, top_k=None, **kwargs):
        captured["top_k"] = top_k
        return {
            "results": [{
                "document_id": 99,
                "chunk_id": 7,
                "page_number": 1,
                "content": long_content,
                "similarity": 0.9,
            }]
        }

    class RecordingProvider:
        def generate(self, prompt):
            captured["prompt"] = prompt
            return "Grounded answer"

    import app.api.chat as chat_module

    monkeypatch.setattr(chat_module.Retriever, "retrieve", fake_retrieve)
    monkeypatch.setattr(chat_module, "get_provider", lambda: RecordingProvider())

    response = client.post("/chat", json={"query": "Summarize this"}, headers=headers)

    assert response.status_code == 200
    assert captured["top_k"] == 3
    assert long_content[:1500] in captured["prompt"]
    assert "THIS_MUST_NOT_REACH_THE_PROMPT" not in captured["prompt"]
    assert response.json()["sources"][0]["content"] == long_content
