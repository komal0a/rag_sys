import os


class Settings:
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./dev.db")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me")


settings = Settings()
