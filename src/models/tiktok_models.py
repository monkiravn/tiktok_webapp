"""Models for TikTok Live Monitoring"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from src.models.user import db


class MonitoredUser(db.Model):
    """Model for tracking TikTok users being monitored"""
    
    __tablename__ = 'monitored_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    room_id = Column(String(100), nullable=True)
    monitoring = Column(Boolean, default=True, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_checked = Column(DateTime, nullable=True)
    
    def __init__(self, username: str, room_id: str = None):
        """Initialize monitored user"""
        self.username = username.replace('@', '')  # Remove @ prefix if present
        self.room_id = room_id
        self.monitoring = True
        self.added_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<MonitoredUser {self.username}>'


class LiveRecording(db.Model):
    """Model for tracking live stream recordings"""
    
    __tablename__ = 'live_recordings'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    room_id = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    telegram_sent = Column(Boolean, default=False, nullable=False)
    status = Column(String(50), default='recording', nullable=False)  # recording, completed, failed
    error_message = Column(Text, nullable=True)
    
    def __init__(self, username: str, room_id: str):
        """Initialize live recording"""
        self.username = username
        self.room_id = room_id
        self.start_time = datetime.utcnow()
        self.status = 'recording'
        self.telegram_sent = False
    
    @property
    def duration_seconds(self) -> int:
        """Calculate recording duration in seconds"""
        if self.end_time and self.start_time:
            return int((self.end_time - self.start_time).total_seconds())
        elif self.start_time:
            return int((datetime.utcnow() - self.start_time).total_seconds())
        return 0
    
    def __repr__(self):
        return f'<LiveRecording {self.username} - {self.start_time}>'