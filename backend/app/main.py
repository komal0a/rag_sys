from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
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
    # Generic exception handlers to avoid leaking internals
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": "Invalid request"})

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # Do not expose exception details
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    app.include_router(health_router, prefix="")
    app.include_router(users_router, prefix="/users", tags=["users"])
    app.include_router(documents_router, prefix="/documents", tags=["documents"])
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(ingest_router, prefix="", tags=["ingest"])
    # search
    try:
        from .api.search import router as search_router
        app.include_router(search_router, prefix="", tags=["search"])
    except Exception:
        # optional
        pass
    try:
        from .api.chat import router as chat_router
        app.include_router(chat_router, prefix="", tags=["chat"])
    except Exception:
        pass
    try:
        from .api.conversations import router as conv_router
        app.include_router(conv_router, prefix="/conversations", tags=["conversations"])
    except Exception:
        pass

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
