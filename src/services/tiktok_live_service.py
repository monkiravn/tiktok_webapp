"""TikTok Live Monitoring Service"""

import os
import re
import json
import time
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from flask import current_app
import requests
from curl_cffi import requests as cf_requests

from src.services.telegram_service import TelegramService


@dataclass
class LiveSession:
    """Data class for tracking live sessions"""
    username: str
    room_id: str
    recording: bool = False
    start_time: Optional[datetime] = None
    file_path: Optional[str] = None
    monitoring: bool = True


class TikTokLiveService:
    """Service for monitoring and recording TikTok live streams"""

    def __init__(self):
        self.BASE_URL = 'https://www.tiktok.com'
        self.WEBCAST_URL = 'https://webcast.tiktok.com'
        self.API_URL = 'https://www.tiktok.com/api-live/user/room/'
        
        self.monitored_users: Dict[str, LiveSession] = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Configure session with proper headers
        self.session = cf_requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def add_user_to_monitor(self, user_input: str) -> Tuple[bool, str]:
        """Add a user to monitoring list"""
        try:
            username, room_id = self._parse_user_input(user_input)
            if not username:
                return False, "Could not extract username from input"
            
            # Check if user exists and get room_id if needed
            if not room_id:
                room_id = self.get_room_id_from_user(username)
                if not room_id:
                    return False, f"Could not find user: {username}"
            
            # Add to monitoring
            self.monitored_users[username] = LiveSession(
                username=username,
                room_id=room_id,
                monitoring=True
            )
            
            # Start monitoring if not already active
            if not self.monitoring_active:
                self.start_monitoring()
            
            return True, f"Added {username} to monitoring list"
            
        except Exception as e:
            current_app.logger.error(f"Error adding user to monitor: {e}")
            return False, f"Error: {str(e)}"

    def remove_user_from_monitor(self, username: str) -> Tuple[bool, str]:
        """Remove a user from monitoring"""
        if username in self.monitored_users:
            # Stop recording if active
            session = self.monitored_users[username]
            if session.recording:
                self._stop_recording(username)
            
            del self.monitored_users[username]
            return True, f"Removed {username} from monitoring"
        
        return False, f"User {username} not in monitoring list"

    def get_monitored_users(self) -> List[Dict]:
        """Get list of monitored users with their status"""
        users = []
        for username, session in self.monitored_users.items():
            is_live = self.is_user_live(username)
            users.append({
                'username': username,
                'room_id': session.room_id,
                'monitoring': session.monitoring,
                'recording': session.recording,
                'is_live': is_live,
                'start_time': session.start_time.isoformat() if session.start_time else None
            })
        return users

    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            current_app.logger.info("TikTok live monitoring started")

    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        current_app.logger.info("TikTok live monitoring stopped")

    def _parse_user_input(self, user_input: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse user input to extract username and/or room_id"""
        user_input = user_input.strip()
        
        # If it's a URL
        if 'tiktok.com' in user_input:
            return self._get_user_from_url(user_input)
        
        # If it's just a username
        username = user_input.replace('@', '')
        return username, None

    def _get_user_from_url(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract username and room_id from TikTok URL"""
        try:
            response = self.session.get(url, allow_redirects=True)
            content = response.text
            
            # Extract username from URL pattern
            username_match = re.search(r'@([^/\?]+)', url)
            username = username_match.group(1) if username_match else None
            
            # Extract room_id from page content
            room_id_match = re.search(r'"roomId":"([^"]+)"', content)
            room_id = room_id_match.group(1) if room_id_match else None
            
            return username, room_id
            
        except Exception as e:
            current_app.logger.error(f"Error parsing URL {url}: {e}")
            return None, None

    def get_room_id_from_user(self, username: str) -> Optional[str]:
        """Get room_id for a given username"""
        try:
            # Clean username
            username = username.replace('@', '')
            
            # Try to get from user profile
            profile_url = f"{self.BASE_URL}/@{username}/live"
            response = self.session.get(profile_url)
            
            # Extract room_id from response
            room_id_match = re.search(r'"roomId":"([^"]+)"', response.text)
            if room_id_match:
                return room_id_match.group(1)
            
            # Alternative method using API endpoint
            api_response = self.session.get(f"{self.API_URL}{username}")
            data = api_response.json()
            
            if 'data' in data and 'room' in data['data']:
                return str(data['data']['room']['id'])
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error getting room_id for {username}: {e}")
            return None

    def is_user_live(self, username: str) -> bool:
        """Check if a user is currently live"""
        try:
            session = self.monitored_users.get(username)
            if not session or not session.room_id:
                return False
            
            # Check if room is alive
            check_url = f"{self.WEBCAST_URL}/webcast/room/check_alive/"
            params = {
                'aid': '1988',
                'region': 'CH',
                'room_ids': session.room_id,
                'user_is_login': 'true'
            }
            
            response = self.session.get(check_url, params=params)
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                return data['data'][0].get('alive', False)
            
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error checking if {username} is live: {e}")
            return False

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                for username, session in list(self.monitored_users.items()):
                    if not session.monitoring:
                        continue
                    
                    is_live = self.is_user_live(username)
                    
                    # Start recording if user went live
                    if is_live and not session.recording:
                        self._start_recording(username)
                    
                    # Stop recording if user stopped being live
                    elif not is_live and session.recording:
                        self._stop_recording(username)
                
                # Wait before next check
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                current_app.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait before retrying

    def _start_recording(self, username: str):
        """Start recording a live stream"""
        try:
            session = self.monitored_users.get(username)
            if not session or session.recording:
                return
            
            current_app.logger.info(f"Starting recording for {username}")
            
            # Create output directory
            output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'recordings')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{username}_{timestamp}.mp4"
            file_path = os.path.join(output_dir, filename)
            
            # Get stream URL
            stream_url = self._get_stream_url(session.room_id)
            if not stream_url:
                current_app.logger.error(f"Could not get stream URL for {username}")
                return
            
            # Start FFmpeg recording process
            self._start_ffmpeg_recording(stream_url, file_path, username)
            
            # Update session
            session.recording = True
            session.start_time = datetime.now()
            session.file_path = file_path
            
        except Exception as e:
            current_app.logger.error(f"Error starting recording for {username}: {e}")

    def _stop_recording(self, username: str):
        """Stop recording a live stream"""
        try:
            session = self.monitored_users.get(username)
            if not session or not session.recording:
                return
            
            current_app.logger.info(f"Stopping recording for {username}")
            
            # Stop FFmpeg process (implementation depends on how you track processes)
            self._stop_ffmpeg_recording(username)
            
            # Send to Telegram if file exists
            if session.file_path and os.path.exists(session.file_path):
                try:
                    telegram_service = TelegramService()
                    telegram_service.send_video_file(session.file_path, username)
                except Exception as e:
                    current_app.logger.error(f"Error sending to Telegram: {e}")
            
            # Update session
            session.recording = False
            session.start_time = None
            
        except Exception as e:
            current_app.logger.error(f"Error stopping recording for {username}: {e}")

    def _get_stream_url(self, room_id: str) -> Optional[str]:
        """Get the actual stream URL for recording"""
        try:
            # This is a simplified version - the actual implementation would need
            # to parse the TikTok live stream URLs which can be complex
            info_url = f"{self.WEBCAST_URL}/webcast/room/info/"
            params = {
                'aid': '1988',
                'room_id': room_id
            }
            
            response = self.session.get(info_url, params=params)
            data = response.json()
            
            # Extract stream URL from response
            # This is where you'd parse the actual stream URLs
            # For now, return a placeholder
            return f"https://pull-flv-l1-tt02.tiktokcdn.com/live/{room_id}/index.m3u8"
            
        except Exception as e:
            current_app.logger.error(f"Error getting stream URL for room {room_id}: {e}")
            return None

    def _start_ffmpeg_recording(self, stream_url: str, output_path: str, username: str):
        """Start FFmpeg recording process"""
        try:
            # FFmpeg command to record stream
            cmd = [
                'ffmpeg',
                '-i', stream_url,
                '-c', 'copy',
                '-f', 'mp4',
                '-y',  # Overwrite output file
                output_path
            ]
            
            # Start process in background (you might want to store the process reference)
            # For now, this is a simplified implementation
            subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        except Exception as e:
            current_app.logger.error(f"Error starting FFmpeg for {username}: {e}")

    def _stop_ffmpeg_recording(self, username: str):
        """Stop FFmpeg recording process"""
        try:
            # This would need to track and terminate the specific FFmpeg process
            # Implementation depends on how you track the processes
            # For now, this is a placeholder
            pass
            
        except Exception as e:
            current_app.logger.error(f"Error stopping FFmpeg for {username}: {e}")