"""
Lightweight evaluation script for local use.

Run with: python -m backend.scripts.evaluate (or python backend/scripts/evaluate.py)
This script seeds an in-memory DB with two documents and chunks and runs a few queries
to show retrieval and grounding behavior.
"""
from app.main import create_app
from app import models
from app.deps import get_db
from app.services.embeddings import FakeEmbeddingProvider
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def run():
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # seed
    u = models.User(email="eval@example.com", hashed_password="x")
    db.add(u); db.commit(); db.refresh(u)
    d1 = models.Document(user_id=u.id, filename="a.pdf", status="uploaded")
    d2 = models.Document(user_id=u.id, filename="b.pdf", status="uploaded")
    db.add_all([d1, d2]); db.commit(); db.refresh(d1); db.refresh(d2)

    p = FakeEmbeddingProvider(dim=8)
    e1 = p.embed_texts(["The sky is blue"])[0]
    e2 = p.embed_texts(["Water is wet"])[0]
    c1 = models.DocumentChunk(document_id=d1.id, chunk_index=0, content="The sky is blue.", embedding=e1)
    c2 = models.DocumentChunk(document_id=d2.id, chunk_index=0, content="Water is wet.", embedding=e2)
    db.add_all([c1, c2]); db.commit()

    from app.services.retrieval import Retriever
    r = Retriever(db)
    queries = ["What color is the sky?", "Is water wet?", "Who wrote Hamlet?"]
    for q in queries:
        out = r.retrieve(q, top_k=2, user_id=u.id)
        print("QUERY:", q)
        print("RESULTS:")
        for res in out["results"]:
            print(res["content"], "sim=", res.get("similarity"))
        print("---")


if __name__ == '__main__':
    run()
