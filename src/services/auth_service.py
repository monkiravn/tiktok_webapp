"""Authentication service for managing user login/logout."""

from functools import wraps

from flask import session, request, redirect, url_for, current_app, flash


class AuthService:
    """Service for handling authentication operations."""

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is currently authenticated."""
        return session.get('authenticated', False)

    @staticmethod
    def login(username: str, password: str) -> bool:
        """Validate login credentials and set session."""
        config_username = current_app.config.get('LOGIN_USERNAME')
        config_password = current_app.config.get('LOGIN_PASSWORD')
        
        if username == config_username and password == config_password:
            session['authenticated'] = True
            session['username'] = username
            return True
        return False

    @staticmethod
    def logout() -> None:
        """Clear user session."""
        session.pop('authenticated', None)
        session.pop('username', None)


def login_required(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not AuthService.is_authenticated():
            flash('Please log in to access this feature.', 'warning')
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function