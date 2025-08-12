"""User repository for database operations."""

from src.models.user import User, db


class UserRepository:
    """Repository for user database operations."""

    @staticmethod
    def get_by_username(username: str) -> User | None:
        """Get user by username."""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def create_user(
        username: str, password: str, role: str = "user", status: str = "pending"
    ) -> User:
        """Create a new user."""
        user = User(username=username, password=password, role=role, status=status)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        """Get user by ID."""
        return User.query.get(user_id)

    @staticmethod
    def update_password(user: User, new_password: str) -> None:
        """Update user password."""
        user.set_password(new_password)
        db.session.commit()

    @staticmethod
    def delete_user(user: User) -> None:
        """Delete a user."""
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def get_all_users() -> list[User]:
        """Get all users."""
        return User.query.all()

    @staticmethod
    def count_users() -> int:
        """Count total number of users."""
        return User.query.count()

    @staticmethod
    def get_pending_users() -> list[User]:
        """Get all pending users."""
        return User.query.filter_by(status="pending").all()

    @staticmethod
    def approve_user(user: User) -> None:
        """Approve a user account."""
        user.approve()
        db.session.commit()

    @staticmethod
    def get_by_role(role: str) -> list[User]:
        """Get users by role."""
        return User.query.filter_by(role=role).all()

    @staticmethod
    def delete_user_by_id(user_id: int) -> bool:
        """Delete a user by ID. Returns True if successful, False if user not found."""
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
