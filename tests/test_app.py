"""Basic tests for the Flask application."""

import pytest

from src.app import create_app


@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app("testing")
    app.config['LOGIN_USERNAME'] = 'testuser'
    app.config['LOGIN_PASSWORD'] = 'testpass'
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def authenticated_client(client):
    """Create a test client with authenticated session."""
    # Login first
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    return client


def test_home_page_redirects_to_login(client):
    """Test the home page redirects to login when unauthenticated."""
    response = client.get("/")
    assert response.status_code == 302
    assert response.location == "/login"


def test_home_page_redirects_to_dashboard_when_authenticated(authenticated_client):
    """Test the home page redirects to dashboard when authenticated."""
    response = authenticated_client.get("/")
    assert response.status_code == 302
    assert response.location == "/dashboard"


def test_dashboard_page(authenticated_client):
    """Test the dashboard page loads when authenticated."""
    response = authenticated_client.get("/dashboard")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_dashboard_requires_authentication(client):
    """Test the dashboard page requires authentication."""
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.location


def test_api_health(client):
    """Test the API health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "tiktok-reup-webapp"
