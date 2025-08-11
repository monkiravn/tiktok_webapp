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
from src.models.tiktok_models import MonitoredUser, LiveRecording
from src.models.user import db
from src.utils.logger_manager import tiktok_logger


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
        
        # Active sessions (runtime state)
        self.active_sessions: Dict[str, LiveSession] = {}
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
        
        # Load existing monitored users from database into active sessions
        self._load_monitored_users()

    def _load_monitored_users(self):
        """Load monitored users from database into active sessions"""
        try:
            # Only load if not already loaded or if we have database access
            from flask import has_app_context
            if not has_app_context():
                # Skip loading if we don't have app context - will be loaded later
                tiktok_logger.info("Skipping user loading - no app context available")
                return
                
            monitored_users = MonitoredUser.query.filter_by(monitoring=True).all()
            for user in monitored_users:
                self.active_sessions[user.username] = LiveSession(
                    username=user.username,
                    room_id=user.room_id,
                    monitoring=user.monitoring
                )
            tiktok_logger.info(f"Loaded {len(monitored_users)} monitored users from database")
        except Exception as e:
            tiktok_logger.error(f"Error loading monitored users: {e}")

    def add_user_to_monitor(self, user_input: str) -> Tuple[bool, str]:
        """Add a user to monitoring list"""
        try:
            username, room_id = self._parse_user_input(user_input)
            if not username:
                return False, "Could not extract username from input"
            
            # Check if user already exists in database
            existing_user = MonitoredUser.query.filter_by(username=username).first()
            if existing_user:
                if existing_user.monitoring:
                    return False, f"User {username} is already being monitored"
                else:
                    # Reactivate monitoring for existing user
                    existing_user.monitoring = True
                    existing_user.last_checked = datetime.utcnow()
                    db.session.commit()
            else:
                # Check if user exists and get room_id if needed
                if not room_id:
                    room_id = self.get_room_id_from_user(username)
                    if not room_id:
                        return False, f"Could not find user: {username}"
                
                # Create new monitored user in database
                new_user = MonitoredUser(username=username, room_id=room_id)
                db.session.add(new_user)
                db.session.commit()
            
            # Add to active sessions
            self.active_sessions[username] = LiveSession(
                username=username,
                room_id=room_id or existing_user.room_id if existing_user else room_id,
                monitoring=True
            )
            
            # Start monitoring if not already active
            if not self.monitoring_active:
                self.start_monitoring()
            
            return True, f"Added {username} to monitoring list"
            
        except Exception as e:
            tiktok_logger.error(f"Error adding user to monitor: {e}")
            return False, f"Error: {str(e)}"

    def remove_user_from_monitor(self, username: str) -> Tuple[bool, str]:
        """Remove a user from monitoring"""
        try:
            # Remove from database
            user = MonitoredUser.query.filter_by(username=username).first()
            if user:
                # Stop recording if active
                if username in self.active_sessions:
                    session = self.active_sessions[username]
                    if session.recording:
                        self._stop_recording(username)
                
                # Remove from database
                db.session.delete(user)
                db.session.commit()
                
                # Remove from active sessions
                if username in self.active_sessions:
                    del self.active_sessions[username]
                
                return True, f"Removed {username} from monitoring"
            
            return False, f"User {username} not in monitoring list"
            
        except Exception as e:
            tiktok_logger.error(f"Error removing user from monitor: {e}")
            return False, f"Error: {str(e)}"

    def get_monitored_users(self) -> List[Dict]:
        """Get list of monitored users with their status"""
        users = []
        try:
            # Get from database to ensure we have the most current data
            monitored_users = MonitoredUser.query.filter_by(monitoring=True).all()
            
            for user in monitored_users:
                # Check if user has an active session
                session = self.active_sessions.get(user.username)
                is_live = False
                recording = False
                start_time = None
                
                if session:
                    is_live = self.is_user_live(user.username)
                    recording = session.recording
                    start_time = session.start_time
                
                users.append({
                    'username': user.username,
                    'room_id': user.room_id,
                    'monitoring': user.monitoring,
                    'recording': recording,
                    'is_live': is_live,
                    'start_time': start_time,
                    'added_at': user.added_at,
                    'last_checked': user.last_checked
                })
            
            return users
            
        except Exception as e:
            tiktok_logger.error(f"Error getting monitored users: {e}")
            return []

    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            tiktok_logger.info("TikTok live monitoring started")

    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        tiktok_logger.info("TikTok live monitoring stopped")

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
        """Extract username and room_id from TikTok URL using improved method"""
        try:
            # Handle mobile URLs and desktop URLs
            response = self.session.get(url, allow_redirects=True, timeout=10)
            
            if response.status_code == 302:  # Redirect might indicate country restrictions
                tiktok_logger.warning(f"Redirect detected for URL {url} - might be country restricted")
            
            content = response.text
            
            # Extract username from URL pattern (supports both mobile and desktop URLs)
            username_patterns = [
                r'@([^/\?]+)/live',  # Standard live URL pattern
                r'tiktok\.com/@([^/\?]+)',  # General profile pattern
                r'"uniqueId":"([^"]+)"',  # From page content
            ]
            
            username = None
            for pattern in username_patterns:
                username_match = re.search(pattern, url)
                if username_match:
                    username = username_match.group(1)
                    break
            
            if not username:
                # Try to extract from page content
                username_match = re.search(r'"uniqueId":"([^"]+)"', content)
                if username_match:
                    username = username_match.group(1)
            
            # Extract room_id from page content
            room_id = None
            room_id_patterns = [
                r'"roomId":"([^"]+)"',
                r'"room_id":"([^"]+)"',
                r'roomId:\"([^"]+)\"',
            ]
            
            for pattern in room_id_patterns:
                room_id_match = re.search(pattern, content)
                if room_id_match:
                    room_id = room_id_match.group(1)
                    break
            
            tiktok_logger.info(f"Extracted from URL {url}: username={username}, room_id={room_id}")
            return username, room_id
            
        except Exception as e:
            tiktok_logger.error(f"Error parsing URL {url}: {e}")
            return None, None

    def get_room_id_from_user(self, username: str) -> Optional[str]:
        """Get room_id for a given username using improved method from reference repo"""
        try:
            # Clean username
            username = username.replace('@', '')
            
            # Use the API endpoint method from reference repo
            response = self.session.get(self.API_URL, params={
                "uniqueId": username,
                "sourceType": 54,
                "aid": 1988
            }, timeout=10)
            
            if response.status_code != 200:
                tiktok_logger.error(f"Failed to get room_id for {username}: HTTP {response.status_code}")
                return None

            data = response.json()
            
            if (data.get('data') and
                    data['data'].get('user') and
                    data['data']['user'].get('roomId')):
                room_id = data['data']['user']['roomId']
                tiktok_logger.info(f"Found room_id {room_id} for user {username}")
                return room_id
            else:
                tiktok_logger.warning(f"No room_id found for user {username}")
                return None
            
        except Exception as e:
            tiktok_logger.error(f"Error getting room_id for {username}: {e}")
            return None

    def is_user_live(self, username: str) -> bool:
        """Check if a user is currently live"""
        try:
            # Update last checked time in database
            user = MonitoredUser.query.filter_by(username=username).first()
            if user:
                user.last_checked = datetime.utcnow()
                db.session.commit()
            
            session = self.active_sessions.get(username)
            if not session or not session.room_id:
                return False
            
            # Check if room is alive using improved method based on reference repo
            check_url = f"{self.WEBCAST_URL}/webcast/room/check_alive/"
            params = {
                'aid': '1988',
                'region': 'CH',
                'room_ids': session.room_id,
                'user_is_login': 'true'
            }
            
            response = self.session.get(check_url, params=params, timeout=10)
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                return data['data'][0].get('alive', False)
            
            return False
            
        except Exception as e:
            tiktok_logger.error(f"Error checking if {username} is live: {e}")
            return False

    def _monitoring_loop(self):
        """Main monitoring loop - runs with application context"""
        # Import here to avoid circular imports
        from src.app import create_app
        import os
        
        # Create application context for database operations
        app = create_app(os.environ.get("FLASK_ENV", "development"))
        
        with app.app_context():
            while self.monitoring_active:
                try:
                    # Get current monitored users from database
                    monitored_users = MonitoredUser.query.filter_by(monitoring=True).all()
                    
                    for user in monitored_users:
                        username = user.username
                        
                        # Ensure user is in active sessions
                        if username not in self.active_sessions:
                            self.active_sessions[username] = LiveSession(
                                username=username,
                                room_id=user.room_id,
                                monitoring=True
                            )
                        
                        session = self.active_sessions[username]
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
                    tiktok_logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(30)  # Wait before retrying

    def _start_recording(self, username: str):
        """Start recording a live stream"""
        try:
            session = self.active_sessions.get(username)
            if not session or session.recording:
                return
            
            tiktok_logger.info(f"Starting recording for {username}")
            
            # Create recording entry in database
            recording = LiveRecording(username=username, room_id=session.room_id)
            db.session.add(recording)
            db.session.commit()
            
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
                tiktok_logger.error(f"Could not get stream URL for {username}")
                recording.status = 'failed'
                recording.error_message = 'Could not get stream URL'
                db.session.commit()
                return
            
            # Start FFmpeg recording process
            self._start_ffmpeg_recording(stream_url, file_path, username)
            
            # Update session and database
            session.recording = True
            session.start_time = datetime.now()
            session.file_path = file_path
            
            recording.file_path = file_path
            db.session.commit()
            
        except Exception as e:
            tiktok_logger.error(f"Error starting recording for {username}: {e}")
            # Update recording status to failed
            try:
                recording = LiveRecording.query.filter_by(
                    username=username, 
                    status='recording'
                ).order_by(LiveRecording.start_time.desc()).first()
                if recording:
                    recording.status = 'failed'
                    recording.error_message = str(e)
                    db.session.commit()
            except:
                pass

    def _stop_recording(self, username: str):
        """Stop recording a live stream"""
        try:
            session = self.active_sessions.get(username)
            if not session or not session.recording:
                return
            
            tiktok_logger.info(f"Stopping recording for {username}")
            
            # Stop FFmpeg process (implementation depends on how you track processes)
            self._stop_ffmpeg_recording(username)
            
            # Update recording in database
            recording = LiveRecording.query.filter_by(
                username=username, 
                status='recording'
            ).order_by(LiveRecording.start_time.desc()).first()
            
            if recording:
                recording.end_time = datetime.utcnow()
                recording.status = 'completed'
                
                # Calculate file size if file exists
                if session.file_path and os.path.exists(session.file_path):
                    recording.file_size = os.path.getsize(session.file_path)
                    
                    # Send to Telegram if configured
                    try:
                        telegram_service = TelegramService()
                        telegram_service.send_video_file(session.file_path, username)
                        recording.telegram_sent = True
                    except Exception as e:
                        tiktok_logger.error(f"Error sending to Telegram: {e}")
                
                db.session.commit()
            
            # Update session
            session.recording = False
            session.start_time = None
            
        except Exception as e:
            tiktok_logger.error(f"Error stopping recording for {username}: {e}")
            # Update recording status to failed
            try:
                recording = LiveRecording.query.filter_by(
                    username=username, 
                    status='recording'
                ).order_by(LiveRecording.start_time.desc()).first()
                if recording:
                    recording.status = 'failed'
                    recording.error_message = str(e)
                    recording.end_time = datetime.utcnow()
                    db.session.commit()
            except:
                pass

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
            tiktok_logger.error(f"Error getting stream URL for room {room_id}: {e}")
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
            tiktok_logger.error(f"Error starting FFmpeg for {username}: {e}")

    def _stop_ffmpeg_recording(self, username: str):
        """Stop FFmpeg recording process"""
        try:
            # This would need to track and terminate the specific FFmpeg process
            # Implementation depends on how you track the processes
            # For now, this is a placeholder
            pass
            
        except Exception as e:
            tiktok_logger.error(f"Error stopping FFmpeg for {username}: {e}")