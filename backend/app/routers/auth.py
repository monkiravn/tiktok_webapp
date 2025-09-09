"""Auth routes: register, login, me."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import create_access_token, get_current_user
from ..db import get_db
from ..models import User
from ..repositories.user_repository import UserRepository
from ..schemas import LoginRequest, TokenResponse, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Annotated[Session, Depends(get_db)]):
    username = payload.username.strip()
    if (
        payload.confirm_password is not None
        and payload.password != payload.confirm_password
    ):
        raise HTTPException(status_code=400, detail="Passwords do not match")
    existing = UserRepository.get_by_username(db, username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = UserRepository.create_user(
        db, username=username, password=payload.password, role="user", status="pending"
    )
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    username = payload.username.strip()
    user = UserRepository.get_by_username(db, username)
    if not user or not user.check_password(payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not user.is_approved():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account pending approval"
        )

    token = create_access_token(
        str(user.id), extra={"username": user.username, "role": user.role}
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
