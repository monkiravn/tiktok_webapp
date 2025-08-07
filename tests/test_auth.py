"""Tests for authentication functionality."""

import pytest

from src.app import create_app
from src.services.auth_service import AuthService
from src.models.user import db
from src.repositories.user_repository import UserRepository


@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app("testing")
    app.config["LOGIN_USERNAME"] = "testuser"
    app.config["LOGIN_PASSWORD"] = "testpass"
    app.config["ADMIN_USERNAME"] = "testuser"
    app.config["ADMIN_PASSWORD"] = "testpass"
    
    with app.app_context():
        # Create test user
        UserRepository.create_user("testuser", "testpass")
        
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def authenticated_client(client):
    """Create a test client with authenticated session."""
    # Login first
    client.post("/login", data={"username": "testuser", "password": "testpass"})
    return client


def test_login_page_get(client):
    """Test login page loads correctly."""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login Required" in response.data
    assert b"username" in response.data
    assert b"password" in response.data


def test_login_successful(client):
    """Test successful login."""
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpass"},
        follow_redirects=True,
    )

    assert response.status_code == 200


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/login", data={"username": "wronguser", "password": "wrongpass"}
    )

    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_login_missing_credentials(client):
    """Test login with missing credentials."""
    response = client.post("/login", data={"username": "", "password": ""})

    assert response.status_code == 200
    assert b"Please enter both username and password" in response.data


def test_logout(authenticated_client):
    """Test logout functionality."""
    response = authenticated_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out successfully" in response.data


def test_dashboard_requires_login(client):
    """Test that dashboard page requires login."""
    response = client.get("/dashboard")
    assert response.status_code == 302  # Redirect to login

    # Follow redirect
    response = client.get("/dashboard", follow_redirects=True)
    assert b"Please log in to access this feature" in response.data
    assert b"Login Required" in response.data


def test_dashboard_accessible_when_logged_in(authenticated_client):
    """Test that dashboard page is accessible when logged in."""
    response = authenticated_client.get("/dashboard")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_api_upload_requires_login(client):
    """Test that API upload requires login."""
    response = client.post("/api/v1/upload")
    assert response.status_code == 302  # Redirect to login


def test_api_upload_accessible_when_logged_in(authenticated_client):
    """Test that API upload is accessible when logged in."""
    response = authenticated_client.post("/api/v1/upload")
    # Should fail with missing file, but not redirect to login
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "No file provided"


def test_api_process_url_requires_login(client):
    """Test that API process URL requires login."""
    response = client.post("/api/v1/process-url")
    assert response.status_code == 302  # Redirect to login


def test_api_download_requires_login(client):
    """Test that API download requires login."""
    response = client.get("/api/v1/download/test.mp4")
    assert response.status_code == 302  # Redirect to login


def test_home_page_redirects_to_login_without_auth(client):
    """Test that home page redirects to login when not authenticated."""
    response = client.get("/")
    assert response.status_code == 302
    assert response.location == "/login"


def test_api_health_accessible_without_login(client):
    """Test that API health endpoint is accessible without login."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"


def test_auth_service_is_authenticated():
    """Test AuthService.is_authenticated() method."""
    app = create_app("testing")

    with app.test_client():
        with app.test_request_context():
            with app.app_context():
                # Not authenticated initially (no session)
                assert not AuthService.is_authenticated()


def test_auth_service_login():
    """Test AuthService.login() method."""
    app = create_app("testing")
    app.config["LOGIN_USERNAME"] = "testuser"
    app.config["LOGIN_PASSWORD"] = "testpass"
    app.config["ADMIN_USERNAME"] = "testuser"
    app.config["ADMIN_PASSWORD"] = "testpass"

    with app.test_client():
        with app.test_request_context():
            with app.app_context():
                # Create test user
                UserRepository.create_user("testuser", "testpass")
                
                # Valid credentials
                assert AuthService.login("testuser", "testpass")

            with app.app_context():
                # Invalid credentials
                assert not AuthService.login("wronguser", "wrongpass")


def test_auth_service_logout():
    """Test AuthService.logout() method."""
    app = create_app("testing")

    with app.test_client():
        with app.test_request_context():
            with app.app_context():
                # Create test user first
                UserRepository.create_user("testuser", "testpass")
                
                # Login first
                app.config["LOGIN_USERNAME"] = "testuser"
                app.config["LOGIN_PASSWORD"] = "testpass"
                AuthService.login("testuser", "testpass")

                # Verify logged in
                assert AuthService.is_authenticated()

                # Logout
                AuthService.logout()
                assert not AuthService.is_authenticated()


def test_login_redirect_next_parameter(client):
    """Test login redirect with next parameter."""
    # Try to access dashboard page, should redirect to login with next parameter
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.location
    assert "next=" in response.location

    # Login with next parameter should redirect back to dashboard
    response = client.post(
        "/login?next=/dashboard",
        data={"username": "testuser", "password": "testpass"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Dashboard" in response.data
