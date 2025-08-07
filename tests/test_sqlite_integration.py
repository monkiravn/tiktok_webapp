"""Tests for SQLite integration and database functionality."""

import pytest

from src.app import create_app
from src.models.user import db
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService


@pytest.fixture
def app():
    """Create and configure a test app for database testing."""
    app = create_app("testing")
    with app.app_context():
        # Clean up any existing users in test db
        db.create_all()
        for user in UserRepository.get_all_users():
            UserRepository.delete_user(user)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


def test_database_user_creation(app):
    """Test that we can create users in the database."""
    with app.app_context():
        # Create a user
        user = UserRepository.create_user("testuser", "testpass")
        assert user.id is not None
        assert user.username == "testuser"
        assert user.check_password("testpass") is True
        assert user.check_password("wrongpass") is False


def test_database_user_retrieval(app):
    """Test that we can retrieve users from the database."""
    with app.app_context():
        # Create a user
        UserRepository.create_user("testuser", "testpass")
        
        # Retrieve user by username
        retrieved_user = UserRepository.get_by_username("testuser")
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"
        
        # Retrieve non-existent user
        non_existent = UserRepository.get_by_username("nonexistent")
        assert non_existent is None


def test_database_authentication_flow(app):
    """Test complete authentication flow using database."""
    with app.app_context():
        # Create a user in database
        UserRepository.create_user("admin", "password123")
        
        # Test authentication using the database
        with app.test_request_context():
            # Valid credentials should work
            assert AuthService.login("admin", "password123") is True
            assert AuthService.is_authenticated() is True
            assert AuthService.get_current_username() == "admin"
            
            # Logout should clear session
            AuthService.logout()
            assert AuthService.is_authenticated() is False
            assert AuthService.get_current_username() is None


def test_database_password_hashing(app):
    """Test that passwords are properly hashed in the database."""
    with app.app_context():
        # Create a user
        user = UserRepository.create_user("testuser", "plaintext_password")
        
        # Password should be hashed, not stored as plaintext
        assert user.password_hash != "plaintext_password"
        assert len(user.password_hash) > 50  # Bcrypt hashes are long
        
        # But user should still be able to authenticate
        assert user.check_password("plaintext_password") is True
        assert user.check_password("wrong_password") is False


def test_database_user_count(app):
    """Test user count functionality."""
    with app.app_context():
        # Initially no users
        assert UserRepository.count_users() == 0
        
        # Create some users
        UserRepository.create_user("user1", "pass1")
        UserRepository.create_user("user2", "pass2")
        
        # Count should be updated
        assert UserRepository.count_users() == 2


def test_web_login_with_database(client, app):
    """Test web login functionality using database backend."""
    with app.app_context():
        # Create admin user in database
        UserRepository.create_user("admin", "password123")
    
    # Test login via web interface
    response = client.post("/login", data={
        "username": "admin",
        "password": "password123"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Should be redirected to dashboard after successful login
    assert b"Dashboard" in response.data


def test_web_login_invalid_credentials_with_database(client, app):
    """Test web login with invalid credentials using database backend."""
    with app.app_context():
        # Create admin user in database
        UserRepository.create_user("admin", "password123")
    
    # Test login with wrong credentials
    response = client.post("/login", data={
        "username": "admin",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_database_initialization_creates_tables(app):
    """Test that database initialization creates the necessary tables."""
    with app.app_context():
        # Tables should exist and be usable
        user = UserRepository.create_user("test", "test")
        assert user.id is not None
        
        # Should be able to query the user
        found_user = UserRepository.get_by_id(user.id)
        assert found_user is not None
        assert found_user.username == "test"