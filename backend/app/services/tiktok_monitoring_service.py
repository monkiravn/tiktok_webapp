"""In-memory state manager for TikTok live monitoring (FastAPI backend copy)."""

import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class MonitoringStatus(Enum):
    WAITING = "waiting"
    RECORDING = "recording"
    STOPPED = "stopped"
    ERROR = "error"


class LiveStatus(Enum):
    OFFLINE = "offline"
    LIVESTREAM = "livestream"
    ERROR = "error"


@dataclass
class MonitoredUser:
    id: str = field(default_factory=lambda: str(uuid4()))
    username: str = ""
    room_id: str | None = None
    monitoring_status: MonitoringStatus = MonitoringStatus.WAITING
    live_status: LiveStatus = LiveStatus.OFFLINE
    last_check: datetime | None = None
    last_recording: str | None = None
    error_message: str | None = None
    recording_start_time: datetime | None = None


class TikTokMonitoringState:
    def __init__(self):
        self._users: dict[str, MonitoredUser] = {}
        self._lock = threading.RLock()
        self._monitoring_active = True

    def add_user(self, username: str) -> str:
        with self._lock:
            for user in self._users.values():
                if user.username.lower() == username.lower():
                    raise ValueError(f"User @{username} is already being monitored")
            user = MonitoredUser(username=username)
            self._users[user.id] = user
            return user.id

    def remove_user(self, user_id: str) -> bool:
        with self._lock:
            if user_id in self._users:
                del self._users[user_id]
                return True
            return False

    def get_all_users(self) -> list[MonitoredUser]:
        with self._lock:
            return list(self._users.values())

    def get_user(self, user_id: str) -> MonitoredUser | None:
        with self._lock:
            return self._users.get(user_id)

    def update_user_status(
        self,
        user_id: str,
        monitoring_status: MonitoringStatus,
        live_status: LiveStatus,
        error_message: str | None = None,
        room_id: str | None = None,
        recording_path: str | None = None,
    ) -> None:
        with self._lock:
            if user_id in self._users:
                user = self._users[user_id]
                user.monitoring_status = monitoring_status
                user.live_status = live_status
                user.last_check = datetime.now()
                user.error_message = error_message
                if room_id:
                    user.room_id = room_id
                if monitoring_status == MonitoringStatus.RECORDING:
                    user.recording_start_time = datetime.now()
                elif monitoring_status in [
                    MonitoringStatus.STOPPED,
                    MonitoringStatus.ERROR,
                ]:
                    user.recording_start_time = None
                if recording_path:
                    user.last_recording = recording_path

    def is_monitoring_active(self) -> bool:
        return self._monitoring_active

    def set_monitoring_active(self, active: bool) -> None:
        self._monitoring_active = active

    def clear_all(self) -> None:
        with self._lock:
            self._users.clear()


monitoring_state = TikTokMonitoringState()
