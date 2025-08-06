"""API views for REST endpoints."""

from flask import Blueprint, jsonify, request, send_file, current_app
import os

from src.services.video_service import VideoService
from src.services.auth_service import login_required

bp = Blueprint("api", __name__)


@bp.route("/health")
def health():
    """Health check endpoint."""
    return jsonify(
        {"status": "healthy", "service": "tiktok-reup-webapp", "version": "1.0.0"}
    )


@bp.route("/upload", methods=["POST"])
@login_required
def upload():
    """API endpoint for video upload."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        video_service = VideoService()
        result = video_service.process_upload(file)

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/process-url", methods=["POST"])
@login_required
def process_url():
    """Process TikTok URL directly."""
    try:
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"error": "URL is required"}), 400

        url = data["url"]
        video_service = VideoService()
        result = video_service.process_url(url)

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/download/<filename>")
@login_required
def download_processed_video(filename):
    """Download processed video file."""
    try:
        video_service = VideoService()
        file_path = video_service.get_processed_video_path(filename)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
            
        # Return file and schedule cleanup after download
        def cleanup_after_download():
            try:
                video_service.cleanup_processed_file(file_path)
            except Exception as e:
                current_app.logger.warning(f"Failed to cleanup after download: {e}")
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='video/mp4'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
