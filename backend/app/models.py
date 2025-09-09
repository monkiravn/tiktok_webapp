"""ORM models for FastAPI backend."""

from __future__ import annotations

from datetime import datetime

import bcrypt
from sqlalchemy import Column, DateTime, Integer, String

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # domain helpers
    def set_password(self, password: str) -> None:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        password_bytes = password.encode("utf-8")
        hash_bytes = self.password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_approved(self) -> bool:
        return self.status == "approved"
