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


def register_and_token(email="rq@example.com", password="pw12345"):
    client.post("/auth/register", json={"email": email, "password": password})
    r = client.post("/auth/login", json={"email": email, "password": password})
    return r.json()["access_token"]


def test_not_enough_information_behavior():
    token = register_and_token()
    headers = {"Authorization": f"Bearer {token}"}
    # No chunks in DB, ask a question
    r = client.post("/chat", json={"query": "What is in the documents?"}, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert "answer" in body
    assert ("not enough" in body["answer"].lower()) or ("I don't have enough" in body["answer"])
