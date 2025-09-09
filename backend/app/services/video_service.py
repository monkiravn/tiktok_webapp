"""Video processing service for FastAPI backend (no Flask dependency)."""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from moviepy import VideoFileClip
from moviepy.video.fx.MirrorX import MirrorX


class VideoService:
    def __init__(
        self, upload_dir: Path, allowed_extensions: set[str] | None = None
    ) -> None:
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_extensions = allowed_extensions or {"mp4", "mkv", "mov"}

    def allowed_file(self, filename: str) -> bool:
        if not filename or "." not in filename:
            return False
        extension = filename.rsplit(".", 1)[1].lower()
        return extension in self.allowed_extensions

    def process_upload(self, filename: str, file_bytes: bytes) -> dict[str, Any]:
        if not self.allowed_file(filename):
            raise ValueError("Invalid file type")

        filepath = self._save_file(filename, file_bytes)

        try:
            result = self._process_video(filepath)
            return result
        finally:
            self._cleanup_file(filepath)

    def _save_file(self, filename: str, file_bytes: bytes) -> str:
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        filepath = str(self.upload_dir / unique_filename)
        with open(filepath, "wb") as f:
            f.write(file_bytes)
        return filepath

    def _process_video(self, filepath: str) -> dict[str, Any]:
        try:
            with VideoFileClip(filepath) as video:
                original_duration = video.duration
                original_size = (video.w, video.h)

                if original_duration <= 2:
                    raise ValueError("Video must be longer than 2 seconds to process")

                trimmed_video = video.subclipped(1, original_duration - 1)

                scaled_width = int(original_size[0] * 1.1)
                scaled_height = int(original_size[1] * 1.1)
                scaled_video = trimmed_video.resized((scaled_width, scaled_height))

                x_center = scaled_width // 2
                y_center = scaled_height // 2
                x1 = x_center - original_size[0] // 2
                y1 = y_center - original_size[1] // 2
                x2 = x1 + original_size[0]
                y2 = y1 + original_size[1]
                zoomed_video = scaled_video.cropped(x1, y1, x2, y2)

                flipped_video = zoomed_video.with_effects([MirrorX()])

                processed_video = flipped_video.without_audio()

                name, ext = os.path.splitext(os.path.basename(filepath))
                output_filename = f"{name}_processed_{uuid.uuid4().hex[:8]}{ext}"
                output_path = str(self.upload_dir / output_filename)

                processed_video.write_videofile(
                    output_path,
                    codec="libx264",
                    audio_codec=None,
                )

                processed_file_size = os.path.getsize(output_path)
                original_file_size = os.path.getsize(filepath)

                return {
                    "original_file": os.path.basename(filepath),
                    "processed_file": output_filename,
                    "original_file_size_mb": round(
                        original_file_size / (1024 * 1024), 2
                    ),
                    "processed_file_size_mb": round(
                        processed_file_size / (1024 * 1024), 2
                    ),
                    "original_duration": round(original_duration, 2),
                    "processed_duration": round(original_duration - 2, 2),
                    "original_size": original_size,
                    "processed_size": original_size,
                    "processing_status": "Success",
                    "processed_at": datetime.now().isoformat(),
                    "download_path": output_path,
                }

        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Failed to process video: {str(e)}") from e

    def get_processed_video_path(self, filename: str) -> str:
        return str(self.upload_dir / filename)

    def cleanup_processed_file(self, filepath: str) -> None:
        self._cleanup_file(filepath)

    def _cleanup_file(self, filepath: str) -> None:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception:
            # Non-fatal cleanup failure
            pass
