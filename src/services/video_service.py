"""Video processing service containing business logic."""

import os
import uuid
from datetime import datetime
from typing import Any

from flask import current_app
from moviepy import VideoFileClip
from moviepy.video.fx.MirrorX import MirrorX
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
            # Clean up original file only (keep processed file for download)
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
        """Process video file according to requirements."""
        try:
            # Load the video
            with VideoFileClip(filepath) as video:
                # Get original properties
                original_duration = video.duration
                original_size = (video.w, video.h)
                
                # Check if video is long enough for trimming (needs at least 2 seconds)
                if original_duration <= 2:
                    raise ValueError("Video must be longer than 2 seconds to process")
                
                # Step 1: Trim video (remove first and last second)
                trimmed_video = video.subclipped(1, original_duration - 1)
                
                # Step 2: Zoom in by 110% while keeping original dimensions
                # Scale to 110% then crop center back to original size
                scaled_width = int(original_size[0] * 1.1)
                scaled_height = int(original_size[1] * 1.1)
                scaled_video = trimmed_video.resized((scaled_width, scaled_height))
                
                # Crop center portion back to original dimensions (zoom effect)
                x_center = scaled_width // 2
                y_center = scaled_height // 2
                x1 = x_center - original_size[0] // 2
                y1 = y_center - original_size[1] // 2
                x2 = x1 + original_size[0]
                y2 = y1 + original_size[1]
                zoomed_video = scaled_video.cropped(x1, y1, x2, y2)
                
                # Step 3: Flip video horizontally
                flipped_video = zoomed_video.with_effects([MirrorX()])
                
                # Step 4: Remove audio
                processed_video = flipped_video.without_audio()
                
                # Generate output filename
                name, ext = os.path.splitext(os.path.basename(filepath))
                output_filename = f"{name}_processed_{uuid.uuid4().hex[:8]}{ext}"
                output_path = os.path.join(current_app.config["UPLOAD_FOLDER"], output_filename)
                
                # Write the processed video
                processed_video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec=None  # No audio
                )
                
                # Get file size of processed video
                processed_file_size = os.path.getsize(output_path)
                original_file_size = os.path.getsize(filepath)
                
                return {
                    "original_file": os.path.basename(filepath),
                    "processed_file": output_filename,
                    "original_file_size_mb": round(original_file_size / (1024 * 1024), 2),
                    "processed_file_size_mb": round(processed_file_size / (1024 * 1024), 2),
                    "original_duration": round(original_duration, 2),
                    "processed_duration": round(original_duration - 2, 2),  # Trimmed 2 seconds
                    "original_size": original_size,
                    "processed_size": original_size,  # Dimensions unchanged after zoom/crop
                    "processing_status": "Success",
                    "processed_at": datetime.now(),
                    "message": "Video processed successfully: zoomed in 110% (original dimensions maintained), flipped horizontally, trimmed 2 seconds, audio removed",
                    "download_path": output_path
                }
                
        except Exception as e:
            current_app.logger.error(f"Error processing video {filepath}: {str(e)}")
            raise ValueError(f"Failed to process video: {str(e)}")

    def _cleanup_file(self, filepath: str) -> None:
        """Remove temporary file."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            current_app.logger.warning(f"Failed to cleanup file {filepath}: {e}")

    def get_processed_video_path(self, filename: str) -> str:
        """Get the full path to a processed video file."""
        return os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    
    def cleanup_processed_file(self, filepath: str) -> None:
        """Remove processed file after download."""
        self._cleanup_file(filepath)
