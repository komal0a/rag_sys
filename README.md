# RAG Platform

A production-ready AI Document Intelligence / RAG platform with FastAPI backend and React frontend.

## Features

- Document ingestion and chunking with vector embeddings
- Semantic search across documents
- Multi-turn chat with context awareness
- JWT-based authentication
- PostgreSQL backend with Alembic migrations
- Docker Compose orchestration

## Local Development

See `backend/README.md` and `frontend/README.md` for development setup.

### Quick Start with Docker

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (especially SECRET_KEY and JWT_SECRET for production)
nano .env

# Start all services
docker-compose up --build
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Database: localhost:5432

## Deployment Readiness

The Docker configuration uses local Ollama:
- `OLLAMA_EMBEDDING_MODEL=nomic-embed-text` for semantic retrieval (768 dimensions)
- `OLLAMA_MODEL=llama3.2:3b` for answer generation

Pull both models before starting the backend:

```bash
ollama pull nomic-embed-text
ollama pull llama3.2:3b
```

### For Production Deployment

The system is **production-ready architecturally** only when configured with:

1. **Real Embedding Provider** (required for semantic search):
   - `EMBEDDING_PROVIDER=ollama`
   - `OLLAMA_EMBEDDING_MODEL=nomic-embed-text`
   - `EMBEDDING_DIM=768`

2. **Real LLM Provider** (required for chat/Q&A):
   - `LLM_PROVIDER=ollama`
   - `OLLAMA_MODEL=llama3.2:3b`

3. **Verify providers are working:**
   ```bash
   # Check embeddings dimension matches provider
   curl -X POST http://localhost:8000/documents/search \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "top_k": 1}'
   
   # Check LLM responses are real (not stub)
   curl -X POST http://localhost:8000/chat \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is in the uploaded documents?"}'
   ```

### Prerequisites

- Docker and Docker Compose
- PostgreSQL 15+ (or use docker-compose)
- Node.js 20+ (for building frontend)
- Python 3.11+ (for building backend)

### Required Environment Variables

Set these before deploying:

```bash
# Database URL (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Security - MUST change these
SECRET_KEY=<generate-a-secure-random-string>
JWT_SECRET=<generate-a-secure-random-string>

# Frontend URL (for CORS)
FRONTEND_URL=https://frontend.example.com

# Backend API URL (frontend needs this)
VITE_API_URL=https://api.example.com

# Optional: file upload settings
UPLOAD_DIR=/data/uploads
MAX_UPLOAD_SIZE_MB=50

# Optional: embeddings provider
EMBEDDING_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIM=768
```

See `.env.example` for all available settings.

### Deployment Steps

1. **Prepare environment file:**
   ```bash
   cp .env.example .env.production
   # Edit .env.production with production values
   export $(cat .env.production | xargs)
   ```

2. **Build and start services:**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **Run database migrations:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

   If old 8-dimensional fake vectors exist, this migration deliberately stops
   without changing data. Back up the database, explicitly remove the derived
   `document_chunks` rows, rerun the migration, then re-ingest every source PDF.

4. **Verify health:**
   ```bash
   curl http://localhost:8000/health
   ```

### Reverse Proxy Configuration

For production, use a reverse proxy (nginx, Apache, etc.):

**Backend API:**
```
http://localhost:8000 → https://api.example.com
```

**Frontend:**
```
http://localhost:3000 → https://example.com
```

### Database Backups

PostgreSQL data is persisted in Docker volume `pgdata`:

```bash
# Backup
docker-compose exec postgres pg_dump -U postgres rag_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres rag_db < backup.sql
```

### Scaling Notes

- Backend can run with multiple workers (configured in Dockerfile)
- Frontend is static files served via Node.js `serve`
- Database should use managed PostgreSQL in production (AWS RDS, etc.)
- File uploads stored in `/app/storage` (mount as persistent volume)

## API Documentation

Interactive API docs available at `http://localhost:8000/docs`

## Testing

```bash
cd backend
pytest -q
```

## Architecture

- **Backend:** FastAPI with SQLAlchemy ORM
- **Database:** PostgreSQL with pgvector for embeddings (JSON fallback for SQLite)
- **Frontend:** React 18 + Vite + TypeScript
- **Migrations:** Alembic for database schema management

## Security

- JWT-based authentication with token expiration
- Password hashing with bcrypt
- CORS configured per environment
- Sensitive errors not exposed to clients
- File upload validation and size limits
- SQL injection protection via ORM

## Troubleshooting

**Database connection errors:** Ensure DATABASE_URL is correct and PostgreSQL is running.

**CORS errors:** Verify FRONTEND_URL matches the actual frontend origin.

**File upload issues:** Check UPLOAD_DIR permissions and UPLOAD_SIZE_MB limits.

**Missing embeddings:** Run `ollama pull nomic-embed-text`, then ensure the pgvector migration has completed.

