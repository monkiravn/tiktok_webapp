"""In-memory state manager for TikTok live monitoring"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4


class MonitoringStatus(Enum):
    """Status of monitoring for a TikTok user"""
    WAITING = "waiting"
    LIVE = "live" 
    RECORDING = "recording"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class MonitoredUser:
    """Represents a monitored TikTok user"""
    id: str = field(default_factory=lambda: str(uuid4()))
    username: str = ""
    room_id: Optional[str] = None
    status: MonitoringStatus = MonitoringStatus.WAITING
    last_check: Optional[datetime] = None
    last_recording: Optional[str] = None
    error_message: Optional[str] = None
    recording_start_time: Optional[datetime] = None
    

class TikTokMonitoringState:
    """In-memory state manager for TikTok live monitoring"""
    
    def __init__(self):
        self._users: Dict[str, MonitoredUser] = {}
        self._lock = threading.RLock()
        self._monitoring_active = True
        
    def add_user(self, username: str) -> str:
        """Add a user to monitoring"""
        with self._lock:
            # Check if user already exists
            for user in self._users.values():
                if user.username.lower() == username.lower():
                    raise ValueError(f"User @{username} is already being monitored")
            
            user = MonitoredUser(username=username)
            self._users[user.id] = user
            return user.id
    
    def remove_user(self, user_id: str) -> bool:
        """Remove a user from monitoring"""
        with self._lock:
            if user_id in self._users:
                del self._users[user_id]
                return True
            return False
    
    def get_all_users(self) -> List[MonitoredUser]:
        """Get all monitored users"""
        with self._lock:
            return list(self._users.values())
    
    def get_user(self, user_id: str) -> Optional[MonitoredUser]:
        """Get a specific user"""
        with self._lock:
            return self._users.get(user_id)
    
    def update_user_status(self, user_id: str, status: MonitoringStatus, 
                          error_message: Optional[str] = None, 
                          room_id: Optional[str] = None,
                          recording_path: Optional[str] = None):
        """Update user status"""
        with self._lock:
            if user_id in self._users:
                user = self._users[user_id]
                user.status = status
                user.last_check = datetime.now()
                user.error_message = error_message
                
                if room_id:
                    user.room_id = room_id
                
                if status == MonitoringStatus.RECORDING:
                    user.recording_start_time = datetime.now()
                elif status in [MonitoringStatus.STOPPED, MonitoringStatus.ERROR]:
                    user.recording_start_time = None
                
                if recording_path:
                    user.last_recording = recording_path
    
    def is_monitoring_active(self) -> bool:
        """Check if monitoring is active"""
        return self._monitoring_active
    
    def set_monitoring_active(self, active: bool):
        """Set monitoring active state"""
        self._monitoring_active = active
    
    def clear_all(self):
        """Clear all monitored users"""
        with self._lock:
            self._users.clear()


# Global instance for the application
monitoring_state = TikTokMonitoringState()