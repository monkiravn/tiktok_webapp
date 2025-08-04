"""Video processing service containing business logic."""

import os
import time
import uuid
from datetime import datetime
from typing import Any

from flask import current_app
from werkzeug.utils import secure_filename


class VideoService:
    """Service for handling video processing operations."""

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file has allowed extension."""
        if not filename or "." not in filename:
            return False

        extension = filename.rsplit(".", 1)[1].lower()
        return extension in current_app.config["ALLOWED_EXTENSIONS"]

    def process_upload(self, file) -> dict[str, Any]:
        """Process uploaded video file."""
        if not self.allowed_file(file.filename):
            raise ValueError("Invalid file type")

        # Save file
        filepath = self._save_file(file)

        try:
            # Process video
            result = self._process_video(filepath)
            return result
        finally:
            # Clean up
            self._cleanup_file(filepath)

    def process_url(self, url: str) -> dict[str, Any]:
        """Process TikTok URL."""
        if "tiktok.com" not in url:
            raise ValueError("Invalid TikTok URL")

        # Placeholder for URL processing
        return {
            "url": url,
            "status": "processed",
            "message": "URL processing coming soon",
        }

    def _save_file(self, file) -> str:
        """Save uploaded file."""
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"

        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(filepath)
        return filepath

    def _process_video(self, filepath: str) -> dict[str, Any]:
        """Process video file."""
        # Simulate processing
        time.sleep(1)

        file_size = os.path.getsize(filepath)
        filename = os.path.basename(filepath)

        return {
            "original_file": filename,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "processing_status": "Success",
            "processed_at": datetime.now(),
            "message": "Video processed successfully",
        }

    def _cleanup_file(self, filepath: str) -> None:
        """Remove temporary file."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            current_app.logger.warning(f"Failed to cleanup file {filepath}: {e}")
