"""User admin endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..db import get_db
from ..models import User
from ..repositories.user_repository import UserRepository
from ..schemas import Message, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserOut])
def list_users(
    _: Annotated[User, Depends(require_admin)], db: Annotated[Session, Depends(get_db)]
):
    return UserRepository.get_all_users(db)


@router.get("/pending", response_model=list[UserOut])
def list_pending_users(
    _: Annotated[User, Depends(require_admin)], db: Annotated[Session, Depends(get_db)]
):
    return UserRepository.get_pending_users(db)


@router.put("/{user_id}/approve", response_model=UserOut)
def approve_user(
    user_id: int,
    _: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    UserRepository.approve_user(db, user)
    db.refresh(user)
    return user


@router.delete("/{user_id}", response_model=Message)
def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400, detail="You cannot delete your own account"
        )
    ok = UserRepository.delete_user_by_id(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return Message(message="User deleted")
