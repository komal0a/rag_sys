import sys
from pathlib import Path
import tempfile
import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

# Ensure backend package is importable when pytest runs from workspace root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app
from app import models
from app.deps import get_db
from app.services.extraction import extract_text_from_pdf, try_extract
from app.services.chunker import chunk_text
from app.services.embeddings import generate_embeddings
from app.core.security import hash_password
from app.core.jwt import create_access_token

from reportlab.pdfgen import canvas

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

# Create tables
models.Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def make_sample_pdf(path: str, text: str = "Hello PDF world"):
    c = canvas.Canvas(path)
    c.setFont("Helvetica", 12)
    c.drawString(72, 720, text)
    c.save()


def register_and_token(email="ingest@example.com", password="pw12345"):
    # Try login first to handle cases where the user already exists in the test DB.
    r = client.post("/auth/login", json={"email": email, "password": password})
    if r.status_code == 200:
        return r.json()["access_token"]
    # otherwise attempt register then login
    client.post("/auth/register", json={"email": email, "password": password})
    r2 = client.post("/auth/login", json={"email": email, "password": password})
    return r2.json()["access_token"]


def test_pdf_extraction_real_pdf():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "sample.pdf")
        make_sample_pdf(path, text="This is a test PDF for extraction")
        text = extract_text_from_pdf(path)
        assert "test PDF" in text or "This is a test" in text


def test_chunking_and_overlap():
    text = "".join([f"word{i} " for i in range(300)])
    chunks = chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) >= 2
    # check overlap: consecutive chunks should share some words
    first = chunks[0].split()
    second = chunks[1].split()
    assert len(set(first).intersection(set(second))) > 0


def test_embeddings_shape_and_determinism():
    texts = ["a short text", "another text"]
    vecs = generate_embeddings(texts, dim=8)
    assert len(vecs) == 2
    assert all(len(v) == 8 for v in vecs)
    # deterministic: repeated call yields same results
    vecs2 = generate_embeddings(texts, dim=8)
    assert vecs == vecs2


def test_ingest_end_to_end_and_persistence():
    # create user and token directly in DB to avoid cross-session timing issues
    db = TestingSessionLocal()
    hp = hash_password("pw12345")
    user = models.User(email="owner2@example.com", hashed_password=hp)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # create sample PDF and attach to a DB document owned by this user
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ingest.pdf")
        make_sample_pdf(path, text="Chunk me into many words for ingestion test")
        doc = models.Document(user_id=user.id, filename="ingest.pdf", file_path=path)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        doc_id = doc.id

        # call ingest
        resp = client.post(f"/ingest/{doc_id}", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["document_id"] == doc_id
        assert data["chunks"] > 0

        # verify chunks persisted
        chunks = db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id == doc_id).all()
        assert len(chunks) == data["chunks"]
        assert all(c.content for c in chunks)
        # embeddings persisted as JSON-like (list)
        assert isinstance(chunks[0].embedding, list)

        db.close()


def test_ingest_auth_and_ownership():
    # create two users directly in DB
    db = TestingSessionLocal()
    hp = hash_password("pw12345")
    userb = models.User(email="userb@example.com", hashed_password=hp)
    usera = models.User(email="usera@example.com", hashed_password=hp)
    db.add_all([userb, usera])
    db.commit()
    db.refresh(userb)
    db.refresh(usera)
    token_a = create_access_token({"sub": str(usera.id)})
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # create doc owned by userb
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "b.pdf")
        make_sample_pdf(path, text="Owner B's document")
        doc = models.Document(user_id=userb.id, filename="b.pdf", file_path=path)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        doc_id = doc.id

        # user A tries to ingest user B's doc -> should 404 (not found for A)
        r = client.post(f"/ingest/{doc_id}", headers=headers_a)
        assert r.status_code == 404
    db.close()


def test_ingest_failure_missing_file():
    # create user and token directly and a doc with missing file
    db = TestingSessionLocal()
    hp = hash_password("pw12345")
    user = models.User(email="missing@example.com", hashed_password=hp)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}
    doc = models.Document(user_id=user.id, filename="nofile.pdf", file_path="/tmp/does/not/exist.pdf")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    doc_id = doc.id
    r = client.post(f"/ingest/{doc_id}", headers=headers)
    assert r.status_code == 400
    db.close()
