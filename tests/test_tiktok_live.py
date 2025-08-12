"""Test TikTok Live Monitoring functionality"""

import pytest
from unittest.mock import patch, MagicMock

from src.services.tiktok_monitoring_service import (
    monitoring_state, 
    MonitoringStatus, 
    MonitoredUser
)
from src.services.tiktok_live_service import tiktok_service


class TestTikTokMonitoring:
    """Test TikTok Live Monitoring features"""
    
    def setup_method(self):
        """Setup before each test"""
        monitoring_state.clear_all()
    
    def test_add_user_to_monitoring(self):
        """Test adding a user to monitoring"""
        username = "testuser123"
        user_id = tiktok_service.add_user(username)
        
        assert user_id is not None
        users = monitoring_state.get_all_users()
        assert len(users) == 1
        assert users[0].username == username
        assert users[0].status == MonitoringStatus.WAITING
    
    def test_remove_user_from_monitoring(self):
        """Test removing a user from monitoring"""
        username = "testuser123"
        user_id = tiktok_service.add_user(username)
        
        removed = tiktok_service.remove_user(user_id)
        assert removed is True
        
        users = monitoring_state.get_all_users()
        assert len(users) == 0
    
    def test_duplicate_user_prevention(self):
        """Test that duplicate users cannot be added"""
        username = "testuser123"
        tiktok_service.add_user(username)
        
        with pytest.raises(ValueError):
            tiktok_service.add_user(username)
    
    def test_monitoring_status(self):
        """Test monitoring status functionality"""
        # Initially not active
        status = tiktok_service.get_monitoring_status()
        assert "active" in status
        assert "users" in status
        assert len(status["users"]) == 0
        
        # Add user
        user_id = tiktok_service.add_user("testuser")
        status = tiktok_service.get_monitoring_status()
        assert len(status["users"]) == 1
        assert status["users"][0]["username"] == "testuser"
    
    def test_settings_management(self):
        """Test settings update functionality"""
        new_settings = {
            "check_interval": 5,
            "telegram_enabled": True,
            "telegram_bot_token": "test_token"
        }
        
        tiktok_service.update_settings(new_settings)
        current_settings = tiktok_service.get_settings()
        
        assert current_settings["check_interval"] == 5
        assert current_settings["telegram_enabled"] is True
        assert current_settings["telegram_bot_token"] == "test_token"
    
    def test_empty_username_validation(self):
        """Test that empty usernames are rejected"""
        with pytest.raises(ValueError):
            tiktok_service.add_user("")
        
        with pytest.raises(ValueError):
            tiktok_service.add_user("   ")
    
    def test_username_cleanup(self):
        """Test that usernames are properly cleaned"""
        user_id = tiktok_service.add_user("  @testuser123  ")
        users = monitoring_state.get_all_users()
        
        assert len(users) == 1
        assert users[0].username == "testuser123"  # @ removed, whitespace trimmed


class TestTikTokMonitoringAPI:
    """Test the Flask API endpoints"""
    
    def setup_method(self):
        """Setup before each test"""
        monitoring_state.clear_all()
    
    def test_api_status_endpoint(self, client):
        """Test the status API endpoint"""
        response = client.get("/live/api/status")
        assert response.status_code == 200
        
        data = response.get_json()
        assert "active" in data
        assert "users" in data
    
    def test_api_add_user_endpoint(self, client):
        """Test adding user via API"""
        response = client.post("/live/api/users", 
                              json={"username": "testuser123"})
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["success"] is True
        assert "user_id" in data
    
    def test_api_add_user_invalid_data(self, client):
        """Test adding user with invalid data"""
        # No username
        response = client.post("/live/api/users", json={})
        assert response.status_code == 400
        
        # Empty username
        response = client.post("/live/api/users", 
                              json={"username": ""})
        assert response.status_code == 400
    
    def test_api_remove_user_endpoint(self, client):
        """Test removing user via API"""
        # First add a user
        add_response = client.post("/live/api/users", 
                                  json={"username": "testuser123"})
        user_id = add_response.get_json()["user_id"]
        
        # Then remove it
        response = client.delete(f"/live/api/users/{user_id}")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["success"] is True
    
    def test_api_remove_nonexistent_user(self, client):
        """Test removing non-existent user"""
        response = client.delete("/live/api/users/nonexistent-id")
        assert response.status_code == 404
    
    def test_api_settings_endpoints(self, client):
        """Test settings API endpoints"""
        # Get settings
        response = client.get("/live/api/settings")
        assert response.status_code == 200
        
        # Update settings
        new_settings = {
            "check_interval": 10,
            "telegram_enabled": True
        }
        response = client.post("/live/api/settings", json=new_settings)
        assert response.status_code == 200
        
        # Verify settings were updated
        response = client.get("/live/api/settings")
        data = response.get_json()
        assert data["check_interval"] == 10
        assert data["telegram_enabled"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])