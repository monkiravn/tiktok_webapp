"""Tests for TikTok Live Monitoring functionality"""

import pytest
from src.app import create_app
from src.services.tiktok_live_service import TikTokLiveService


@pytest.fixture
def app():
    """Create test app."""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def tiktok_service(app):
    """Create TikTok service instance."""
    with app.app_context():
        return TikTokLiveService()


def test_tiktok_service_initialization(tiktok_service):
    """Test TikTok service can be initialized."""
    assert tiktok_service is not None
    assert tiktok_service.BASE_URL == 'https://www.tiktok.com'
    assert tiktok_service.WEBCAST_URL == 'https://webcast.tiktok.com'


def test_parse_username_input(tiktok_service):
    """Test parsing username input."""
    # Test username without @
    username, room_id = tiktok_service._parse_user_input('testuser')
    assert username == 'testuser'
    assert room_id is None
    
    # Test username with @
    username, room_id = tiktok_service._parse_user_input('@testuser')
    assert username == 'testuser'
    assert room_id is None


def test_tiktok_live_route_requires_auth(client):
    """Test that TikTok live route requires authentication."""
    response = client.get('/tiktok-live')
    assert response.status_code == 302  # Redirect to login


def test_tiktok_live_api_requires_auth(client):
    """Test that TikTok live API endpoints require authentication."""
    response = client.post('/api/v1/tiktok-live/add-user')
    assert response.status_code == 302  # Redirect to login
    
    response = client.get('/api/v1/tiktok-live/monitored-users')
    assert response.status_code == 302  # Redirect to login


def test_add_user_api_with_auth(client, app):
    """Test adding user with authentication."""
    with app.test_request_context():
        # Mock authentication
        with client.session_transaction() as session:
            session['authenticated'] = True
            session['username'] = 'admin'
        
        # Test missing user_input
        response = client.post('/api/v1/tiktok-live/add-user', 
                             json={})
        assert response.status_code == 400
        
        # Test empty user_input
        response = client.post('/api/v1/tiktok-live/add-user', 
                             json={'user_input': ''})
        assert response.status_code == 400
        
        # Test valid user_input (this will fail in actual implementation due to network calls)
        response = client.post('/api/v1/tiktok-live/add-user', 
                             json={'user_input': 'testuser'})
        # Should return 500 due to network error in test environment
        assert response.status_code == 500


def test_get_monitored_users_api_with_auth(client, app):
    """Test getting monitored users with authentication."""
    with app.test_request_context():
        # Mock authentication
        with client.session_transaction() as session:
            session['authenticated'] = True
            session['username'] = 'admin'
        
        response = client.get('/api/v1/tiktok-live/monitored-users')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'success' in data
        assert 'users' in data
        assert data['success'] is True
        assert isinstance(data['users'], list)