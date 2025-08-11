"""Cookie management utilities for TikTok Live Service"""

import json
import os
from typing import Dict, Optional
from src.utils.logger_manager import tiktok_logger


def read_cookies() -> Dict[str, str]:
    """
    Loads the cookies from config file and returns them.
    Similar to Michele0303/tiktok-live-recorder implementation.
    """
    try:
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate to config directory
        config_path = os.path.join(current_dir, "..", "config", "cookies.json")
        config_path = os.path.normpath(config_path)
        
        if not os.path.exists(config_path):
            tiktok_logger.warning(f"Cookies file not found at {config_path}, creating default")
            create_default_cookies_file(config_path)
        
        with open(config_path, "r") as f:
            cookies = json.load(f)
            tiktok_logger.info("Cookies loaded successfully")
            return cookies
            
    except Exception as e:
        tiktok_logger.error(f"Error loading cookies: {e}")
        # Return default cookies if loading fails
        return {
            "sessionid_ss": "",
            "tt-target-idc": "useast2a"
        }


def create_default_cookies_file(config_path: str) -> None:
    """Create default cookies.json file"""
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        default_cookies = {
            "sessionid_ss": "",
            "tt-target-idc": "useast2a"
        }
        
        with open(config_path, "w") as f:
            json.dump(default_cookies, f, indent=2)
            
        tiktok_logger.info(f"Created default cookies file at {config_path}")
        
    except Exception as e:
        tiktok_logger.error(f"Error creating default cookies file: {e}")


def save_cookies(cookies: Dict[str, str]) -> bool:
    """
    Save cookies to the config file
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "..", "config", "cookies.json")
        config_path = os.path.normpath(config_path)
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, "w") as f:
            json.dump(cookies, f, indent=2)
            
        tiktok_logger.info("Cookies saved successfully")
        return True
        
    except Exception as e:
        tiktok_logger.error(f"Error saving cookies: {e}")
        return False


def get_cookie_value(cookie_name: str) -> Optional[str]:
    """
    Get a specific cookie value by name
    """
    cookies = read_cookies()
    return cookies.get(cookie_name)


def set_cookie_value(cookie_name: str, cookie_value: str) -> bool:
    """
    Set a specific cookie value and save to file
    """
    try:
        cookies = read_cookies()
        cookies[cookie_name] = cookie_value
        return save_cookies(cookies)
    except Exception as e:
        tiktok_logger.error(f"Error setting cookie {cookie_name}: {e}")
        return False