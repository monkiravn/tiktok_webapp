"""Telegram Service for sending files and messages"""

import os
from typing import Optional

from pyrogram import Client
from flask import current_app


class TelegramService:
    """Service for Telegram integration"""

    def __init__(self):
        self.api_id = current_app.config.get('TELEGRAM_API_ID')
        self.api_hash = current_app.config.get('TELEGRAM_API_HASH')
        self.bot_token = current_app.config.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = current_app.config.get('TELEGRAM_CHAT_ID')
        
    def is_configured(self) -> bool:
        """Check if Telegram is properly configured"""
        return all([self.api_id, self.api_hash, self.bot_token, self.chat_id])
    
    def send_video_file(self, file_path: str, username: str) -> bool:
        """Send a video file to the configured Telegram chat"""
        if not self.is_configured():
            current_app.logger.warning("Telegram not configured, skipping file send")
            return False
        
        if not os.path.exists(file_path):
            current_app.logger.error(f"File not found: {file_path}")
            return False
        
        try:
            with Client(
                "tiktok_bot",
                api_id=self.api_id,
                api_hash=self.api_hash,
                bot_token=self.bot_token
            ) as app:
                # Send the video file
                message = f"🔴 Live recording from @{username}"
                app.send_video(
                    chat_id=self.chat_id,
                    video=file_path,
                    caption=message
                )
                
                current_app.logger.info(f"Successfully sent {file_path} to Telegram")
                return True
                
        except Exception as e:
            current_app.logger.error(f"Error sending file to Telegram: {e}")
            return False
    
    def send_message(self, message: str) -> bool:
        """Send a text message to the configured Telegram chat"""
        if not self.is_configured():
            current_app.logger.warning("Telegram not configured, skipping message send")
            return False
        
        try:
            with Client(
                "tiktok_bot",
                api_id=self.api_id,
                api_hash=self.api_hash,
                bot_token=self.bot_token
            ) as app:
                app.send_message(
                    chat_id=self.chat_id,
                    text=message
                )
                
                current_app.logger.info(f"Successfully sent message to Telegram")
                return True
                
        except Exception as e:
            current_app.logger.error(f"Error sending message to Telegram: {e}")
            return False