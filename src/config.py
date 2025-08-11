import os

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application Configuration"""

    SECRET_KEY: str = "dev-secret-key"
    DEBUG: bool = False
    TESTING: bool = False

    UPLOAD_FOLDER: str = Field(
        default_factory=lambda: os.path.join(os.getcwd(), "uploads")
    )
    MAX_CONTENT_LENGTH: int = 20 * 1024 * 1024  # 20 MB
    ALLOWED_EXTENSIONS: set[str] = {"mp4", "mkv", "mov"}

    FLASK_ENV: str = "development"

    HOST: str = "0.0.0.0"
    PORT: int = 5000

    # Database settings
    DATABASE_URL: str = Field(
        default_factory=lambda: f"sqlite:///{os.path.join(os.getcwd(), 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Authentication settings (for backward compatibility and seeding)
    LOGIN_USERNAME: str = "admin"
    LOGIN_PASSWORD: str = "password123"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "password123"

    # TikTok Live Monitoring settings
    TIKTOK_MONITORING_ENABLED: bool = True
    TIKTOK_CHECK_INTERVAL: int = 60  # Seconds between checks

    # Telegram integration settings
    TELEGRAM_API_ID: str | None = None
    TELEGRAM_API_HASH: str | None = None
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None

    @validator("UPLOAD_FOLDER", pre=True)
    def resolve_upload_folder(cls, v):
        """Resolve upload folder path"""
        if not os.path.isabs(v):
            return os.path.join(os.getcwd(), v)
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    # Ensure folder exists
    def to_dict(self):
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        return self.dict()


class ProductionConfig(Config):
    SECRET_KEY: str = "super-secret-key"
    DEBUG: bool = False
    FLASK_ENV: str = "production"


class DevelopmentConfig(Config):
    DEBUG: bool = True
    FLASK_ENV: str = "development"


class TestingConfig(Config):
    TESTING: bool = True
    DEBUG: bool = True
    FLASK_ENV: str = "testing"
    DATABASE_URL: str = "sqlite:///:memory:"  # Use in-memory database for testing


configurations = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(env: str | None = None) -> Config:
    """Get configuration class based on environment"""
    if env is None:
        # Try to get from environment variable first
        env = os.getenv("FLASK_ENV", "development")

    config_class = configurations.get(env)
    if not config_class:
        raise ValueError(f"Invalid configuration name: {env}")
    return config_class()
