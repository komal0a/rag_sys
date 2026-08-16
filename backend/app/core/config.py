import os


class Settings:
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./dev.db")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production")
    # JWT settings
    JWT_SECRET: str = os.environ.get("JWT_SECRET", os.environ.get("SECRET_KEY", "change-me-in-production"))
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")
    JWT_EXPIRES_IN: int = int(os.environ.get("JWT_EXPIRES_IN", 60 * 60 * 24))  # seconds
    # Upload settings (Milestone 5)
    UPLOAD_DIR: str = os.environ.get("UPLOAD_DIR", "storage/documents")
    MAX_UPLOAD_SIZE_MB: int = int(os.environ.get("MAX_UPLOAD_SIZE_MB", 10))
    # RAG settings
    DEFAULT_TOP_K: int = int(os.environ.get("DEFAULT_TOP_K", 5))
    RETRIEVAL_SIMILARITY_THRESHOLD: float = float(os.environ.get("RETRIEVAL_SIMILARITY_THRESHOLD", 0.0))
    # CORS settings
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:3000")


settings = Settings()
