"""Basic tests for the Flask application."""

import pytest

from src.app import create_app


@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app("testing")
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


def test_home_page(client):
    """Test the home page loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"TikTok Re-Upload WebApp" in response.data


def test_upload_page(client):
    """Test the upload page loads."""
    response = client.get("/upload")
    assert response.status_code == 200
    assert b"Upload Video" in response.data


def test_about_page(client):
    """Test the about page loads."""
    response = client.get("/about")
    assert response.status_code == 200
    assert b"About TikTok Re-Upload WebApp" in response.data


def test_api_health(client):
    """Test the API health endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "tiktok-reup-webapp"
