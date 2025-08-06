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

    # Authentication settings
    LOGIN_USERNAME: str = "admin"
    LOGIN_PASSWORD: str = "password123"

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


configurations = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(env: str = None) -> Config:
    """Get configuration class based on environment"""
    if env is None:
        # Try to get from environment variable first
        env = os.getenv("FLASK_ENV", "development")

    config_class = configurations.get(env)
    if not config_class:
        raise ValueError(f"Invalid configuration name: {env}")
    return config_class()
