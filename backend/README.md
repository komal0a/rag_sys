# Backend

Run locally:

```
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Production start:

```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

Run tests:

```
pytest -q
```

Database Migrations
-------------------

Initialize database (development with SQLite):

```
# Creates tables automatically on startup
uvicorn app.main:app --reload
```

With PostgreSQL, use Alembic:

```
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# View migration status
alembic current
```

Embedding & Retrieval
---------------------

**Development/Testing Only:**

This project uses a pluggable embedding provider. By default a deterministic
`FakeEmbeddingProvider` is used for tests. The fake provider:
- Does NOT perform real semantic search
- Is deterministic (same input → same output)  
- Works without external dependencies
- Is suitable ONLY for development and testing

Run unit tests with fake embeddings (SQLite):
```
pytest tests/test_api.py -v
```

**Production Configuration:**

For real semantic search, you MUST configure a real embedding provider.

### OpenAI Embeddings (Recommended)

Set these environment variables in `.env`:

```bash
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-...  # From https://platform.openai.com/api-keys
EMBEDDING_MODEL=text-embedding-3-small  # or text-embedding-3-large
EMBEDDING_DIM=1536  # CRITICAL: Must match model output!
```

**Model dimensions (MUST MATCH EMBEDDING_DIM):**
- `text-embedding-3-small` → 1536 dimensions
- `text-embedding-3-large` → 3072 dimensions
- `text-embedding-ada-002` → 1536 dimensions

⚠️ **Critical:** If EMBEDDING_DIM doesn't match the provider's output, vector storage and queries will fail.

### Integration Tests with PostgreSQL + pgvector

To run tests with real embeddings and PostgreSQL:

```bash
# Set up environment
export DATABASE_URL=postgresql://user:pass@localhost:5432/rag_test
export EMBEDDING_PROVIDER=openai
export OPENAI_API_KEY=sk-...

# Ensure pgvector extension is installed in Postgres
psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run tests
pytest tests/ -v
```

Storage: We store vectors in Postgres using the `pgvector` extension.
For development/local tests, SQLite + JSON fallback is used.

LLM Provider Configuration (Chat API)
-------------------------------------

The `/chat` endpoint generates responses using a pluggable LLM provider.

**Development/Testing Only:**

```bash
LLM_PROVIDER=fake  # Returns stub responses, no API calls
```

**Production Configuration:**

For real Q&A responses, use OpenAI:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...  # Same account as embeddings
LLM_MODEL=gpt-4-turbo  # or gpt-3.5-turbo for lower cost
```

Supported models:
- `gpt-4-turbo` — Most capable, higher cost
- `gpt-4` — Full version of GPT-4
- `gpt-3.5-turbo` — Fast and low-cost, recommended for most applications

**Note:** LLM provider must be configured for `/chat` endpoint to work. Without it, responses will be generic stubs.

See `app/services/llm.py` to add custom providers (Anthropic, Azure, Llama, etc.).

Production Configuration
------------------------

### Database & Security (Required for All Deployments)

**Environment Variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Random secret for security (change-me-in-production is unsafe!)
- `JWT_SECRET` - Secret for JWT token signing (change-me-in-production is unsafe!)
- `FRONTEND_URL` - Frontend origin for CORS (e.g., https://example.com)

### AI Features (Optional but Recommended)

**For semantic search to work (real retrieval):**
- `EMBEDDING_PROVIDER=openai`
- `OPENAI_API_KEY=sk-...`
- `EMBEDDING_MODEL=text-embedding-3-small` or similar
- `EMBEDDING_DIM=1536` (or correct value for your model)

**For chat/Q&A to work (real responses):**
- `LLM_PROVIDER=openai`
- `LLM_MODEL=gpt-3.5-turbo` or similar
- Uses same `OPENAI_API_KEY`

⚠️ **Without these, the system uses fake providers and cannot perform real RAG.**

### File Upload & RAG (Optional)

- `UPLOAD_DIR` - File upload directory (default: storage/documents)
- `MAX_UPLOAD_SIZE_MB` - Max file size (default: 10)
- `DEFAULT_TOP_K` - Results per query (default: 5)
- `RETRIEVAL_SIMILARITY_THRESHOLD` - Minimum similarity score (default: 0.0)

### JWT Settings (Optional)

- `JWT_ALGORITHM` - Token algorithm (default: HS256)
- `JWT_EXPIRES_IN` - Token expiration in seconds (default: 86400 = 1 day)

See `.env.example` for all available settings.

Checklist for Production Deployment

File Upload
-----------

Uploaded files are stored on disk at the path specified by `UPLOAD_DIR`. 
In production, this should be a persistent volume.

- Files are validated (PDF only)
- Names are sanitized and randomized for security
- Size is limited by `MAX_UPLOAD_SIZE_MB`
