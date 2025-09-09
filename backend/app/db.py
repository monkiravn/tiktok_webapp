"""SQLAlchemy engine and session for FastAPI backend."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from . import models  # noqa: F401 - ensure models are imported

    Base.metadata.create_all(bind=engine)
    seed_admin()


def seed_admin() -> None:
    """Create default admin user if it doesn't exist."""
    from .models import User

    with SessionLocal() as db:
        existing = (
            db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
        )
        if not existing:
            user = User(
                username=settings.ADMIN_USERNAME,
                password_hash="",  # will be set below
                role="admin",
                status="approved",
            )
            user.set_password(settings.ADMIN_PASSWORD)
            db.add(user)
            db.commit()
