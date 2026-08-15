# Backend

Run locally:

```
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests:

```
pytest -q
```

Embedding & Retrieval
---------------------

This project uses a pluggable embedding provider. By default a deterministic
`FakeEmbeddingProvider` is used for tests. You can configure a real provider
via environment variables in `.env`:

- `EMBEDDING_PROVIDER` - `fake` (default) or `openai`
- `EMBEDDING_MODEL` - model name for the provider
- `EMBEDDING_DIM` - embedding vector dimension (defaults vary by provider)

We store vectors in Postgres using the `pgvector` extension when available.
For local tests SQLite + JSON fallback is used.

To run integration tests that exercise Postgres + pgvector, set `DATABASE_URL`
to a running Postgres instance and ensure the `vector` extension is available.
