"""Tests for TikTok Live monitoring functionality."""

import pytest
from unittest.mock import patch, MagicMock
import json

from src.services.tiktok_live_service import TikTokLiveService, TikTokLiveMonitor


class TestTikTokLiveService:
    """Test TikTokLiveService functionality."""
    
    def test_live_service_initialization(self):
        """Test service initialization."""
        service = TikTokLiveService()
        assert service.monitors == {}
        assert isinstance(service.settings, dict)
        assert "check_interval" in service.settings
        assert "output_dir" in service.settings
        
    def test_add_monitor_success(self):
        """Test adding a monitor successfully."""
        service = TikTokLiveService()
        
        # Mock the TikTokLiveMonitor to avoid actual monitoring
        with patch('src.services.tiktok_live_service.TikTokLiveMonitor') as mock_monitor_class:
            mock_monitor = MagicMock()
            mock_monitor.start_monitoring.return_value = True
            mock_monitor_class.return_value = mock_monitor
            
            success, message = service.add_monitor("testuser")
            
            assert success is True
            assert "successfully" in message.lower()
            assert "testuser" in service.monitors
            mock_monitor.start_monitoring.assert_called_once()
            
    def test_add_monitor_duplicate(self):
        """Test adding a duplicate monitor."""
        service = TikTokLiveService()
        
        with patch('src.services.tiktok_live_service.TikTokLiveMonitor') as mock_monitor_class:
            mock_monitor = MagicMock()
            mock_monitor.start_monitoring.return_value = True
            mock_monitor_class.return_value = mock_monitor
            
            # Add first monitor
            service.add_monitor("testuser")
            
            # Try to add duplicate
            success, message = service.add_monitor("testuser")
            
            assert success is False
            assert "already being monitored" in message
            
    def test_remove_monitor_success(self):
        """Test removing a monitor successfully."""
        service = TikTokLiveService()
        
        with patch('src.services.tiktok_live_service.TikTokLiveMonitor') as mock_monitor_class:
            mock_monitor = MagicMock()
            mock_monitor.start_monitoring.return_value = True
            mock_monitor_class.return_value = mock_monitor
            
            # Add monitor first
            service.add_monitor("testuser")
            
            # Remove monitor
            success, message = service.remove_monitor("testuser")
            
            assert success is True
            assert "successfully" in message.lower()
            assert "testuser" not in service.monitors
            mock_monitor.stop_monitoring.assert_called_once()
            
    def test_remove_monitor_not_found(self):
        """Test removing a non-existent monitor."""
        service = TikTokLiveService()
        
        success, message = service.remove_monitor("nonexistent")
        
        assert success is False
        assert "not being monitored" in message
        
    def test_get_all_monitors(self):
        """Test getting all monitors."""
        service = TikTokLiveService()
        
        with patch('src.services.tiktok_live_service.TikTokLiveMonitor') as mock_monitor_class:
            mock_monitor = MagicMock()
            mock_monitor.start_monitoring.return_value = True
            mock_monitor.get_status_info.return_value = {
                "username": "testuser",
                "status": "monitoring",
                "start_time": "2023-01-01T00:00:00",
                "last_check": None,
                "is_running": True,
                "recording_file": None
            }
            mock_monitor_class.return_value = mock_monitor
            
            # Add monitor
            service.add_monitor("testuser")
            
            # Get all monitors
            monitors = service.get_all_monitors()
            
            assert len(monitors) == 1
            assert monitors[0]["username"] == "testuser"
            assert monitors[0]["status"] == "monitoring"
            
    def test_settings_persistence(self):
        """Test settings saving and loading."""
        service = TikTokLiveService()
        
        test_settings = {
            "check_interval": 10,
            "duration": 3600,
            "output_dir": "/test/path",
            "use_telegram": True,
            "telegram_config": {"api_id": "test"}
        }
        
        # Mock file operations
        with patch('builtins.open', create=True) as mock_open:
            with patch('json.dump') as mock_json_dump:
                success = service.save_settings(test_settings)
                
                assert success is True
                mock_open.assert_called_once()
                mock_json_dump.assert_called_once_with(test_settings, mock_open().__enter__(), indent=2)


class TestTikTokLiveMonitor:
    """Test TikTokLiveMonitor functionality."""
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        settings = {"check_interval": 5, "output_dir": "/test"}
        monitor = TikTokLiveMonitor("testuser", settings)
        
        assert monitor.username == "testuser"
        assert monitor.settings == settings
        assert monitor.status == "stopped"
        assert monitor.process is None
        assert monitor.is_running is False
        
    def test_monitor_status_info(self):
        """Test getting monitor status info."""
        settings = {"check_interval": 5}
        monitor = TikTokLiveMonitor("testuser", settings)
        
        status = monitor.get_status_info()
        
        assert status["username"] == "testuser"
        assert status["status"] == "stopped"
        assert status["start_time"] is None
        assert status["last_check"] is None
        assert status["is_running"] is False
        assert status["recording_file"] is None


def test_api_endpoints(client):
    """Test live monitoring API endpoints."""
    # Login first
    with client.session_transaction() as sess:
        sess['authenticated'] = True
        sess['username'] = 'admin'
    
    # Test get monitors endpoint
    response = client.get('/api/v1/live/monitors')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'monitors' in data
    
    # Test add monitor endpoint
    response = client.post('/api/v1/live/monitors', 
                          json={'username': 'testuser'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    
    # Test get settings endpoint
    response = client.get('/api/v1/live/settings')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'settings' in data