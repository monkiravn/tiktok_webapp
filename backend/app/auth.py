"""JWT auth utilities and dependencies."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import User


def create_access_token(
    subject: str, extra: dict | None = None, expires_minutes: int | None = None
) -> str:
    to_encode = {"sub": subject, "iat": datetime.now(tz=UTC)}
    if extra:
        to_encode.update(extra)
    expire = datetime.now(tz=UTC) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRES_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError as e:  # noqa: B904
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        ) from e
    except jwt.InvalidTokenError as e:  # noqa: B904
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from e


bearer_scheme = HTTPBearer(auto_error=False)


def _resolve_token(
    request: Request, credentials: HTTPAuthorizationCredentials | None
) -> str | None:
    # Prefer Authorization header (Bearer token)
    if credentials and credentials.scheme.lower() == "bearer":
        return credentials.credentials
    # Fallback: allow token via query for dev tools (?token=...)
    token = request.query_params.get("token")
    if token:
        return token
    return None


def get_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    token = _resolve_token(request, credentials)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    payload = decode_token(token)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject"
        )
    try:
        user_id = int(sub)
    except ValueError as e:  # noqa: B904
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject"
        ) from e

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    if not user.is_approved():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not approved"
        )
    return user


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user
