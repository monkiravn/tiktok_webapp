"""FastAPI settings and configuration."""

import os
from pathlib import Path

from pydantic import Field
from pydantic.functional_validators import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings for the FastAPI backend."""

    # App
    APP_NAME: str = "tiktok-reup-backend"
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ALLOW_ORIGINS: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    # Paths
    BASE_DIR: Path = Field(default_factory=lambda: Path(os.getcwd()))
    UPLOAD_FOLDER: Path = Field(default_factory=lambda: Path(os.getcwd()) / "uploads")

    # Database
    DATABASE_URL: str = Field(
        default_factory=lambda: f"sqlite:///{Path(os.getcwd()) / 'app.db'}"
    )

    # Auth seed (admin)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "password123"

    # Auth/JWT
    SECRET_KEY: str = Field(
        default_factory=lambda: os.environ.get("SECRET_KEY", "dev-secret-key")
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def ensure_dirs(self) -> None:
        self.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    # Allow CSV string in env for CORS origins
    @field_validator("CORS_ALLOW_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):  # type: ignore[no-untyped-def]
        if isinstance(v, str):
            # split by comma and strip spaces
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


settings = Settings()
settings.ensure_dirs()
