"""Test user registration and admin approval functionality."""

import pytest
from src.app import create_app
from src.models.user import db
from src.repositories.user_repository import UserRepository


@pytest.fixture
def app():
    """Create and configure test app."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


def test_user_registration_creates_pending_user(client):
    """Test that user registration creates a pending user."""
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    
    # Should redirect to login after successful registration
    assert response.status_code == 302
    assert response.location.endswith('/login')
    
    # User should exist in database with pending status
    user = UserRepository.get_by_username('testuser')
    assert user is not None
    assert user.role == 'user'
    assert user.status == 'pending'
    assert not user.is_approved()


def test_pending_user_cannot_login(client, app):
    """Test that pending users cannot log in."""
    with app.app_context():
        # Create a pending user
        UserRepository.create_user('pendinguser', 'password123', role='user', status='pending')
    
    # Try to login with pending user
    response = client.post('/login', data={
        'username': 'pendinguser',
        'password': 'password123'
    })
    
    # Should stay on login page with error message
    assert response.status_code == 200
    assert b'pending admin approval' in response.data


def test_approved_user_can_login(client, app):
    """Test that approved users can log in."""
    with app.app_context():
        # Create an approved user
        UserRepository.create_user('approveduser', 'password123', role='user', status='approved')
    
    # Try to login with approved user
    response = client.post('/login', data={
        'username': 'approveduser',
        'password': 'password123'
    })
    
    # Should redirect to dashboard
    assert response.status_code == 302
    assert response.location.endswith('/dashboard')


def test_admin_can_access_user_management(client, app):
    """Test that admin can access user management page."""
    with app.app_context():
        # Create an admin user
        UserRepository.create_user('admin', 'password123', role='admin', status='approved')
    
    # Login as admin
    client.post('/login', data={
        'username': 'admin',
        'password': 'password123'
    })
    
    # Access user management page
    response = client.get('/admin/users')
    assert response.status_code == 200
    assert b'User Management' in response.data


def test_regular_user_cannot_access_user_management(client, app):
    """Test that regular users cannot access user management page."""
    with app.app_context():
        # Create a regular user
        UserRepository.create_user('regularuser', 'password123', role='user', status='approved')
    
    # Login as regular user
    client.post('/login', data={
        'username': 'regularuser',
        'password': 'password123'
    })
    
    # Try to access user management page
    response = client.get('/admin/users')
    # Should redirect to dashboard with error
    assert response.status_code == 302
    assert response.location.endswith('/dashboard')


def test_admin_can_approve_users(client, app):
    """Test that admin can approve pending users."""
    with app.app_context():
        # Create admin and pending user
        UserRepository.create_user('admin', 'password123', role='admin', status='approved')
        pending_user = UserRepository.create_user('pendinguser', 'password123', role='user', status='pending')
        pending_user_id = pending_user.id
    
    # Login as admin
    client.post('/login', data={
        'username': 'admin',
        'password': 'password123'
    })
    
    # Approve the pending user
    response = client.post(f'/admin/approve_user/{pending_user_id}')
    assert response.status_code == 302
    
    # Check that user is now approved
    with app.app_context():
        user = UserRepository.get_by_id(pending_user_id)
        assert user.status == 'approved'
        assert user.is_approved()


def test_get_pending_users(app):
    """Test getting pending users."""
    with app.app_context():
        # Create users with different statuses
        UserRepository.create_user('admin', 'password123', role='admin', status='approved')
        UserRepository.create_user('approveduser', 'password123', role='user', status='approved')
        UserRepository.create_user('pendinguser1', 'password123', role='user', status='pending')
        UserRepository.create_user('pendinguser2', 'password123', role='user', status='pending')
        
        # Get pending users
        pending_users = UserRepository.get_pending_users()
        assert len(pending_users) == 2
        assert all(user.status == 'pending' for user in pending_users)


def test_user_role_methods(app):
    """Test user role and status methods."""
    with app.app_context():
        # Create admin user
        admin = UserRepository.create_user('admin', 'password123', role='admin', status='approved')
        assert admin.is_admin()
        assert admin.is_approved()
        
        # Create regular user
        user = UserRepository.create_user('user', 'password123', role='user', status='pending')
        assert not user.is_admin()
        assert not user.is_approved()
        
        # Approve user
        user.approve()
        assert user.is_approved()
        assert user.status == 'approved'