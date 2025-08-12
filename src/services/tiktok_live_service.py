"""TikTok Live Recording Service."""

import json
import os
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.config import get_config


class TikTokLiveMonitor:
    """Individual monitor for a TikTok user."""
    
    def __init__(self, username: str, settings: Dict):
        self.username = username
        self.settings = settings
        self.status = "stopped"
        self.process = None
        self.start_time = None
        self.last_check = None
        self.recording_file = None
        self.thread = None
        self.is_running = False
        
    def start_monitoring(self):
        """Start monitoring this user."""
        if self.is_running:
            return False
            
        self.is_running = True
        self.status = "monitoring"
        self.start_time = datetime.now()
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        return True
        
    def stop_monitoring(self):
        """Stop monitoring this user."""
        self.is_running = False
        self.status = "stopped"
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception:
                pass
        self.process = None
        
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            try:
                self.last_check = datetime.now()
                if self._check_if_live():
                    self._start_recording()
                else:
                    self._ensure_not_recording()
                    
                # Wait for the configured interval
                interval = self.settings.get("check_interval", 5) * 60  # Convert to seconds
                time.sleep(interval)
            except Exception as e:
                print(f"Error in monitor loop for {self.username}: {e}")
                time.sleep(60)  # Wait a minute before retrying
                
    def _check_if_live(self) -> bool:
        """Check if the user is currently live."""
        # For now, we'll implement a simple check
        # In a real implementation, this would use the TikTok API or scraping
        return False  # Placeholder
        
    def _start_recording(self):
        """Start recording the live stream."""
        if self.process and self.process.poll() is None:
            return  # Already recording
            
        try:
            cli_path = TikTokLiveService.get_cli_path()
            output_dir = self.settings.get("output_dir", "/tmp/recordings")
            os.makedirs(output_dir, exist_ok=True)
            
            cmd = [
                "python", f"{cli_path}/main.py",
                "-user", self.username,
                "-mode", "automatic",
                "-output", output_dir,
                "-automatic_interval", str(self.settings.get("check_interval", 5))
            ]
            
            # Add duration if specified
            if self.settings.get("duration"):
                cmd.extend(["-duration", str(self.settings["duration"])])
                
            # Add telegram if enabled
            if self.settings.get("use_telegram", False):
                cmd.append("-telegram")
                
            self.process = subprocess.Popen(
                cmd,
                cwd=f"{cli_path}",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.status = "recording"
            
        except Exception as e:
            print(f"Error starting recording for {self.username}: {e}")
            self.status = "error"
            
    def _ensure_not_recording(self):
        """Ensure we're not recording when user is not live."""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process = None
            self.status = "monitoring"
            
    def get_status_info(self) -> Dict:
        """Get current status information."""
        return {
            "username": self.username,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "is_running": self.is_running,
            "recording_file": self.recording_file
        }


class TikTokLiveService:
    """Service for managing TikTok live recording monitors."""
    
    def __init__(self):
        self.monitors: Dict[str, TikTokLiveMonitor] = {}
        self.settings = self._load_settings()
        
    @staticmethod
    def get_cli_path() -> str:
        """Get path to the TikTok live recorder CLI."""
        config = get_config()
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cli_path = os.path.join(base_path, "third_party", "tiktok-live-recorder", "src")
        return cli_path
        
    def _load_settings(self) -> Dict:
        """Load settings from file."""
        config = get_config()
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        settings_file = os.path.join(base_path, "tiktok_live_settings.json")
        
        default_settings = {
            "check_interval": 5,  # minutes
            "duration": None,  # seconds, None for unlimited
            "output_dir": os.path.join(base_path, "recordings"),
            "use_telegram": False,
            "telegram_config": {},
            "cookies": {}
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            
        return default_settings
        
    def save_settings(self, settings: Dict) -> bool:
        """Save settings to file."""
        try:
            config = get_config()
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            settings_file = os.path.join(base_path, "tiktok_live_settings.json")
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            self.settings = settings
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
            
    def add_monitor(self, username: str) -> Tuple[bool, str]:
        """Add a new monitor for a username."""
        if username in self.monitors:
            return False, "User is already being monitored"
            
        try:
            monitor = TikTokLiveMonitor(username, self.settings)
            if monitor.start_monitoring():
                self.monitors[username] = monitor
                return True, "Monitor added successfully"
            else:
                return False, "Failed to start monitoring"
        except Exception as e:
            return False, f"Error adding monitor: {str(e)}"
            
    def remove_monitor(self, username: str) -> Tuple[bool, str]:
        """Remove a monitor for a username."""
        if username not in self.monitors:
            return False, "User is not being monitored"
            
        try:
            monitor = self.monitors[username]
            monitor.stop_monitoring()
            del self.monitors[username]
            return True, "Monitor removed successfully"
        except Exception as e:
            return False, f"Error removing monitor: {str(e)}"
            
    def get_all_monitors(self) -> List[Dict]:
        """Get status of all monitors."""
        return [monitor.get_status_info() for monitor in self.monitors.values()]
        
    def get_monitor_status(self, username: str) -> Optional[Dict]:
        """Get status of a specific monitor."""
        if username in self.monitors:
            return self.monitors[username].get_status_info()
        return None
        
    def stop_all_monitors(self):
        """Stop all monitors."""
        for monitor in self.monitors.values():
            monitor.stop_monitoring()
        self.monitors.clear()
        
    def update_cli_tool(self) -> Tuple[bool, str]:
        """Update the CLI tool from GitHub."""
        try:
            cli_base_path = os.path.dirname(self.get_cli_path())
            
            # If directory exists, pull updates
            if os.path.exists(os.path.join(cli_base_path, ".git")):
                result = subprocess.run(
                    ["git", "pull"], 
                    cwd=cli_base_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return True, "CLI tool updated successfully"
                else:
                    return False, f"Failed to update: {result.stderr}"
            else:
                # Clone the repository
                parent_dir = os.path.dirname(cli_base_path)
                os.makedirs(parent_dir, exist_ok=True)
                
                result = subprocess.run([
                    "git", "clone",
                    "https://github.com/Michele0303/tiktok-live-recorder.git",
                    cli_base_path
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True, "CLI tool installed successfully"
                else:
                    return False, f"Failed to install: {result.stderr}"
                    
        except Exception as e:
            return False, f"Error updating CLI tool: {str(e)}"


# Global instance
_live_service = None

def get_live_service() -> TikTokLiveService:
    """Get the global live service instance."""
    global _live_service
    if _live_service is None:
        _live_service = TikTokLiveService()
    return _live_service