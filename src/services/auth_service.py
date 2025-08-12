"""Authentication service for managing user login/logout."""

from functools import wraps

from flask import session, request, redirect, url_for, current_app, flash

from src.repositories.user_repository import UserRepository


class AuthService:
    """Service for handling authentication operations."""

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is currently authenticated."""
        return session.get('authenticated', False)

    @staticmethod
    def login(username: str, password: str) -> bool:
        """Validate login credentials against database and set session."""
        # Get user from database
        user = UserRepository.get_by_username(username)
        
        if user and user.check_password(password):
            # Check if user is approved
            if not user.is_approved():
                return False  # Don't allow login for pending users
            
            session['authenticated'] = True
            session['username'] = username
            session['user_id'] = user.id
            session['role'] = user.role
            return True
        return False

    @staticmethod
    def logout() -> None:
        """Clear user session."""
        session.pop('authenticated', None)
        session.pop('username', None)
        session.pop('user_id', None)
        session.pop('role', None)

    @staticmethod
    def get_current_user_id() -> int | None:
        """Get current authenticated user ID."""
        return session.get('user_id')

    @staticmethod
    def get_current_username() -> str | None:
        """Get current authenticated username."""
        return session.get('username')
    
    @staticmethod
    def get_current_user_role() -> str | None:
        """Get current authenticated user role."""
        return session.get('role')
    
    @staticmethod
    def is_admin() -> bool:
        """Check if current user is admin."""
        return session.get('role') == 'admin'


def login_required(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthService.is_authenticated():
            flash('Please log in to access this feature.', 'warning')
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthService.is_authenticated():
            flash('Please log in to access this feature.', 'warning')
            return redirect(url_for('main.login', next=request.url))
        if not AuthService.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function