"""TikTok Live Recording Service for Flask Application"""

import os
import threading
import time
from typing import Optional, Dict, Any
import logging

from src.services.tiktok_monitoring_service import (
    monitoring_state, 
    MonitoringStatus, 
    MonitoredUser
)


class TikTokLiveService:
    """Service for monitoring and recording TikTok live streams"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._monitoring_thread: Optional[threading.Thread] = None
        self._should_stop = threading.Event()
        self._settings = self._get_default_settings()
        
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings for monitoring"""
        return {
            "check_interval": 2,  # minutes
            "recording_duration": None,  # None = until stream ends
            "output_directory": "recordings",
            "telegram_enabled": False,
            "telegram_bot_token": "",
            "telegram_chat_id": "",
            "cookies": {}
        }
    
    def start_monitoring(self):
        """Start the monitoring service"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self.logger.warning("Monitoring is already running")
            return False
            
        self._should_stop.clear()
        monitoring_state.set_monitoring_active(True)
        
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitoring_thread.start()
        
        self.logger.info("TikTok live monitoring started")
        return True
    
    def stop_monitoring(self):
        """Stop the monitoring service"""
        monitoring_state.set_monitoring_active(False)
        self._should_stop.set()
        
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)
            
        self.logger.info("TikTok live monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self._should_stop.is_set() and monitoring_state.is_monitoring_active():
            try:
                users = monitoring_state.get_all_users()
                
                for user in users:
                    if self._should_stop.is_set():
                        break
                        
                    self._check_user_live_status(user)
                    
                # Wait for the specified interval
                wait_time = self._settings["check_interval"] * 60  # Convert to seconds
                self._should_stop.wait(wait_time)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                self._should_stop.wait(30)  # Wait 30 seconds before retrying
    
    def _check_user_live_status(self, user: MonitoredUser):
        """Check if a user is currently live"""
        try:
            # For now, simulate the check - in a real implementation, 
            # this would use the TikTok API to check live status
            is_live = self._simulate_live_check(user.username)
            
            if is_live and user.status != MonitoringStatus.RECORDING:
                self._start_recording(user)
            elif not is_live and user.status == MonitoringStatus.RECORDING:
                self._stop_recording(user)
            elif not is_live:
                monitoring_state.update_user_status(
                    user.id, 
                    MonitoringStatus.WAITING
                )
                
        except Exception as e:
            self.logger.error(f"Error checking live status for @{user.username}: {e}")
            monitoring_state.update_user_status(
                user.id,
                MonitoringStatus.ERROR,
                error_message=str(e)
            )
    
    def _simulate_live_check(self, username: str) -> bool:
        """Simulate live check - replace with actual TikTok API call"""
        # This is a placeholder - in real implementation, integrate with TikTok API
        import random
        return random.random() < 0.1  # 10% chance of being live for demo
    
    def _start_recording(self, user: MonitoredUser):
        """Start recording a live stream"""
        try:
            self.logger.info(f"Starting recording for @{user.username}")
            
            # Update status to recording
            monitoring_state.update_user_status(
                user.id,
                MonitoringStatus.RECORDING,
                room_id="simulated_room_id"
            )
            
            # In a real implementation, this would start the actual recording
            # using the TikTok recorder module
            
        except Exception as e:
            self.logger.error(f"Error starting recording for @{user.username}: {e}")
            monitoring_state.update_user_status(
                user.id,
                MonitoringStatus.ERROR,
                error_message=str(e)
            )
    
    def _stop_recording(self, user: MonitoredUser):
        """Stop recording a live stream"""
        try:
            self.logger.info(f"Stopping recording for @{user.username}")
            
            # Simulate recording path
            recording_path = f"recordings/{user.username}_{int(time.time())}.mp4"
            
            monitoring_state.update_user_status(
                user.id,
                MonitoringStatus.STOPPED,
                recording_path=recording_path
            )
            
            # Send to Telegram if enabled
            if self._settings["telegram_enabled"]:
                self._send_to_telegram(recording_path, user.username)
                
        except Exception as e:
            self.logger.error(f"Error stopping recording for @{user.username}: {e}")
            monitoring_state.update_user_status(
                user.id,
                MonitoringStatus.ERROR,
                error_message=str(e)
            )
    
    def _send_to_telegram(self, recording_path: str, username: str):
        """Send recording to Telegram"""
        try:
            # Placeholder for Telegram integration
            self.logger.info(f"Sending recording to Telegram: {recording_path}")
            
        except Exception as e:
            self.logger.error(f"Error sending to Telegram: {e}")
    
    def add_user(self, username: str) -> str:
        """Add a user to monitoring"""
        # Clean username (remove @ if present)
        username = username.strip().lstrip('@')
        
        if not username:
            raise ValueError("Username cannot be empty")
            
        user_id = monitoring_state.add_user(username)
        self.logger.info(f"Added user @{username} to monitoring")
        return user_id
    
    def remove_user(self, user_id: str) -> bool:
        """Remove a user from monitoring"""
        removed = monitoring_state.remove_user(user_id)
        if removed:
            self.logger.info(f"Removed user from monitoring")
        return removed
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        users = monitoring_state.get_all_users()
        
        return {
            "active": monitoring_state.is_monitoring_active(),
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "status": user.status.value,
                    "last_check": user.last_check.isoformat() if user.last_check else None,
                    "error_message": user.error_message,
                    "last_recording": user.last_recording,
                    "recording_start_time": user.recording_start_time.isoformat() if user.recording_start_time else None
                }
                for user in users
            ]
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update monitoring settings"""
        self._settings.update(settings)
        self.logger.info("Monitoring settings updated")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return self._settings.copy()


# Global service instance
tiktok_service = TikTokLiveService()