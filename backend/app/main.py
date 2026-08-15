from fastapi import FastAPI
from .api.health import router as health_router
from .api.users import router as users_router
from .api.documents import router as documents_router
from .api.auth import router as auth_router
from .api.ingest import router as ingest_router
from app.core.config import settings
from app.database import init_db
import os


def create_app() -> FastAPI:
    app = FastAPI(title="RAG Platform Backend")
    app.include_router(health_router, prefix="")
    app.include_router(users_router, prefix="/users", tags=["users"])
    app.include_router(documents_router, prefix="/documents", tags=["documents"])
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(ingest_router, prefix="", tags=["ingest"])

    @app.on_event("startup")
    def startup_event():
        # For local development with SQLite, create tables automatically.
        if settings.DATABASE_URL.startswith("sqlite"):
            init_db()

    @app.get("/ready")
    def ready():
        return {"status": "ready"}

    return app


# Backwards-compatible single module app
app = create_app()
