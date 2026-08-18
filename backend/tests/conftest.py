"""Keep unit tests deterministic and independent of a running Ollama service."""

import os


os.environ["EMBEDDING_PROVIDER"] = "fake"
os.environ["EMBEDDING_DIM"] = "8"
# SQLAlchemy tests supply their own in-memory engine, so keep the model's
# SQLite fallback column type instead of pgvector's Postgres-only type.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
