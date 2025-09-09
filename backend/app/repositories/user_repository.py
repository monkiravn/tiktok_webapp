"""User repository using SQLAlchemy Session."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import User


class UserRepository:
    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        password: str,
        role: str = "user",
        status: str = "pending",
    ) -> User:
        user = User(username=username, role=role, status=status)
        user.set_password(password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    @staticmethod
    def update_password(db: Session, user: User, new_password: str) -> None:
        user.set_password(new_password)
        db.commit()

    @staticmethod
    def delete_user(db: Session, user: User) -> None:
        db.delete(user)
        db.commit()

    @staticmethod
    def get_all_users(db: Session) -> list[User]:
        return db.query(User).all()

    @staticmethod
    def count_users(db: Session) -> int:
        return db.query(User).count()

    @staticmethod
    def get_pending_users(db: Session) -> list[User]:
        return db.query(User).filter(User.status == "pending").all()

    @staticmethod
    def approve_user(db: Session, user: User) -> None:
        user.status = "approved"
        db.commit()

    @staticmethod
    def get_by_role(db: Session, role: str) -> list[User]:
        return db.query(User).filter(User.role == role).all()

    @staticmethod
    def delete_user_by_id(db: Session, user_id: int) -> bool:
        user = db.get(User, user_id)
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
