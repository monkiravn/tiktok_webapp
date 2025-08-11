"""Logger manager for TikTok Live Service - adapted from Michele0303/tiktok-live-recorder"""

import logging
from typing import Optional


class MaxLevelFilter(logging.Filter):
    """Filter that only allows log records up to a specified maximum level."""
    
    def __init__(self, max_level):
        super().__init__()
        self.max_level = max_level

    def filter(self, record):
        # Only accept records whose level number is <= self.max_level
        return record.levelno <= self.max_level


class TikTokLiveLogger:
    """Singleton logger manager for TikTok Live Service background operations."""
    
    _instance: Optional['TikTokLiveLogger'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TikTokLiveLogger, cls).__new__(cls)
            cls._instance.logger = None
            cls._instance.setup_logger()
        return cls._instance

    def setup_logger(self):
        """Setup the logger with INFO and ERROR handlers."""
        if self.logger is None:
            self.logger = logging.getLogger('tiktok_live_service')
            self.logger.setLevel(logging.INFO)

            # Clear any existing handlers to avoid duplicates
            self.logger.handlers.clear()

            # 1) INFO handler - for general information
            info_handler = logging.StreamHandler()
            info_handler.setLevel(logging.INFO)
            info_format = '[TikTok Live] %(asctime)s - %(message)s'
            info_datefmt = '%Y-%m-%d %H:%M:%S'
            info_formatter = logging.Formatter(info_format, info_datefmt)
            info_handler.setFormatter(info_formatter)

            # Add a filter to exclude ERROR level (and above) messages
            info_handler.addFilter(MaxLevelFilter(logging.INFO))

            self.logger.addHandler(info_handler)

            # 2) ERROR handler - for errors and warnings
            error_handler = logging.StreamHandler()
            error_handler.setLevel(logging.ERROR)
            error_format = '[TikTok Live ERROR] %(asctime)s - %(message)s'
            error_datefmt = '%Y-%m-%d %H:%M:%S'
            error_formatter = logging.Formatter(error_format, error_datefmt)
            error_handler.setFormatter(error_formatter)

            self.logger.addHandler(error_handler)

    def info(self, message: str):
        """Log an INFO-level message."""
        self.logger.info(message)

    def error(self, message: str):
        """Log an ERROR-level message."""
        self.logger.error(message)

    def warning(self, message: str):
        """Log a WARNING-level message."""
        self.logger.warning(message)


# Global logger instance for easy import
tiktok_logger = TikTokLiveLogger()