"""Service for managing TikTok live streams (FastAPI backend copy)."""

from __future__ import annotations

import threading
import time
from typing import Any

from ..third_party import TikTokAPI
from .tiktok_monitoring_service import (
    LiveStatus,
    MonitoredUser,
    MonitoringStatus,
    monitoring_state,
)


class TikTokLiveService:
    def __init__(self, proxy=None, cookies=None) -> None:
        self.tiktok_api = TikTokAPI(proxy=proxy, cookies=cookies)
        self._monitoring_thread: threading.Thread | None = None
        self._should_stop = threading.Event()

    def start_monitoring(self) -> bool:
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            print("Monitoring is already running")
            return False
        self._should_stop.clear()
        monitoring_state.set_monitoring_active(True)
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self._monitoring_thread.start()
        print("TikTok live monitoring started")
        return True

    def stop_monitoring(self) -> None:
        monitoring_state.set_monitoring_active(False)
        self._should_stop.set()
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)
        print("TikTok live monitoring stopped")

    def _monitoring_loop(self) -> None:
        while (
            not self._should_stop.is_set() and monitoring_state.is_monitoring_active()
        ):
            try:
                users = monitoring_state.get_all_users()
                for user in users:
                    if self._should_stop.is_set():
                        break
                    self._check_user_live_status(user)
                self._should_stop.wait(5)
            except Exception as e:  # noqa: BLE001
                print(f"Error in monitoring loop: {e}")
                self._should_stop.wait(30)

    def _check_user_live_status(self, user: MonitoredUser) -> None:
        try:
            room_id = user.room_id or self.get_room_id_from_user(user.username)
            is_live = self.live_check(room_id)
            user.room_id = room_id
            if is_live and user.monitoring_status != MonitoringStatus.RECORDING:
                print(f"User @{user.username} is live, starting recording")
                self._start_recording(user)
            elif not is_live and user.monitoring_status == MonitoringStatus.RECORDING:
                print(f"User @{user.username} is no longer live, stopping recording")
                self._stop_recording(user)
            elif not is_live:
                print(f"User @{user.username} is offline")
                monitoring_state.update_user_status(
                    user.id,
                    monitoring_status=MonitoringStatus.WAITING,
                    live_status=LiveStatus.OFFLINE,
                )
            else:
                print(f"User @{user.username} is still live, no action needed")
        except Exception as e:  # noqa: BLE001
            print(f"Error checking live status for @{user.username}: {e}")
            monitoring_state.update_user_status(
                user.id,
                MonitoringStatus.ERROR,
                LiveStatus.ERROR,
                error_message=str(e),
            )

    def _start_recording(self, user: MonitoredUser) -> None:
        try:
            monitoring_state.update_user_status(
                user.id, MonitoringStatus.RECORDING, live_status=LiveStatus.LIVESTREAM
            )
            print(f"Starting recording for @{user.username}")
        except Exception as e:  # noqa: BLE001
            print(f"Error starting recording for @{user.username}: {e}")
            monitoring_state.update_user_status(
                user.id,
                MonitoringStatus.ERROR,
                live_status=LiveStatus.LIVESTREAM,
                error_message=str(e),
            )

    def _stop_recording(self, user: MonitoredUser) -> None:
        try:
            print(f"Stopping recording for @{user.username}")
            recording_path = f"recordings/{user.username}_{int(time.time())}.mp4"
            monitoring_state.update_user_status(
                user.id,
                MonitoringStatus.STOPPED,
                live_status=LiveStatus.OFFLINE,
                recording_path=recording_path,
            )
        except Exception as e:  # noqa: BLE001
            print(f"Error stopping recording for @{user.username}: {e}")
            monitoring_state.update_user_status(
                user.id,
                MonitoringStatus.ERROR,
                live_status=LiveStatus.OFFLINE,
                error_message=str(e),
            )

    def get_room_id_from_user(self, username: str) -> str:
        return self.tiktok_api.get_room_id_from_user(username)

    def get_room_and_user_from_url(self, live_url: str) -> tuple:
        user, room_id = self.tiktok_api.get_room_and_user_from_url(live_url)
        return user, room_id

    def live_check(self, room_id: str) -> bool:
        return self.tiktok_api.is_room_alive(room_id)

    def add_user(self, username: str) -> str:
        username = username.strip().lstrip("@")
        if not username:
            raise ValueError("Username cannot be empty")
        user_id = monitoring_state.add_user(username)
        print(f"Added user @{username} to monitoring")
        return user_id

    def remove_user(self, user_id: str) -> bool:
        removed = monitoring_state.remove_user(user_id)
        if removed:
            print("Removed user from monitoring")
        return removed

    def get_monitoring_status(self) -> dict[str, Any]:
        users = monitoring_state.get_all_users()
        return {
            "active": monitoring_state.is_monitoring_active(),
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "room_id": user.room_id,
                    "monitoring_status": user.monitoring_status.value,
                    "live_status": user.live_status.value,
                    "last_check": user.last_check.isoformat()
                    if user.last_check
                    else None,
                    "error_message": user.error_message,
                    "last_recording": user.last_recording,
                    "recording_start_time": user.recording_start_time.isoformat()
                    if user.recording_start_time
                    else None,
                }
                for user in users
            ],
        }


def read_cookies_from_file(path: str) -> dict | None:  # simple local util
    import json

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


cookies = read_cookies_from_file("cookies.json")
tiktok_service = TikTokLiveService(cookies=cookies)
