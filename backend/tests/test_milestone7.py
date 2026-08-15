import sys
from pathlib import Path
import os
import tempfile

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app
from app import models
from app.deps import get_db
from app.services.embeddings import FakeEmbeddingProvider
from app.services.retrieval import Retriever


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


def test_fake_provider_and_retriever_ordering():
    # use a fake provider to create deterministic embeddings
    p = FakeEmbeddingProvider(dim=8)
    query = "important query"
    qemb = p.embed_texts([query])[0]

    db = TestingSessionLocal()
    # create user and document
    user = models.User(email="u1@example.com", hashed_password="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    doc = models.Document(user_id=user.id, filename="d.pdf")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # close match
    c1 = models.DocumentChunk(document_id=doc.id, chunk_index=0, content="close", embedding=qemb)
    # far match (different vector)
    c2 = models.DocumentChunk(document_id=doc.id, chunk_index=1, content="far", embedding=[0.0] * 8)
    db.add_all([c1, c2])
    db.commit()
    db.refresh(c1)
    db.refresh(c2)

    retriever = Retriever(db)
    out = retriever.retrieve(query, top_k=2, user_id=user.id)
    assert out["results"][0]["chunk_id"] == c1.id
    assert out["results"][1]["chunk_id"] == c2.id


def test_search_api_auth_and_user_isolation():
    # create two users and two docs; ensure one cannot see other's chunks
    db = TestingSessionLocal()
    # create user a via API so we can login
    client.post("/auth/register", json={"email": "a@example.com", "password": "pw12345"})
    r = client.post("/auth/login", json={"email": "a@example.com", "password": "pw12345"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    # find the user id
    u1 = db.query(models.User).filter(models.User.email == "a@example.com").first()
    # create a second user directly
    u2 = models.User(email="b@example.com", hashed_password="x")
    db.add(u2)
    db.commit()
    db.refresh(u2)
    d1 = models.Document(user_id=u1.id, filename="a.pdf")
    d2 = models.Document(user_id=u2.id, filename="b.pdf")
    db.add_all([d1, d2])
    db.commit()
    db.refresh(d1)
    db.refresh(d2)

    # embeddings
    p = FakeEmbeddingProvider(dim=8)
    emb1 = p.embed_texts(["q"])[0]
    emb2 = p.embed_texts(["other"])[0]
    ch1 = models.DocumentChunk(document_id=d1.id, chunk_index=0, content="u1chunk", embedding=emb1)
    ch2 = models.DocumentChunk(document_id=d2.id, chunk_index=0, content="u2chunk", embedding=emb2)
    db.add_all([ch1, ch2])
    db.commit()

    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/documents/search", json={"query": "q", "top_k": 5}, headers=headers)
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert any(r["content"] == "u1chunk" for r in results)
    assert all(r["document_id"] == d1.id for r in results)

    # unauthenticated
    resp2 = client.post("/documents/search", json={"query": "q"})
    assert resp2.status_code == 401
