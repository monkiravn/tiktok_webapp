"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    message: str


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=6)
    confirm_password: str | None = None


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
