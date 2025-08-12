"""API views for REST endpoints."""

from flask import Blueprint, jsonify, request, send_file, current_app
import os

from src.services.video_service import VideoService
from src.services.auth_service import login_required
from src.services.tiktok_live_service import get_live_service

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


# TikTok Live Monitoring API endpoints

@bp.route("/live/monitors", methods=["GET"])
@login_required
def get_live_monitors():
    """Get all live monitors."""
    try:
        live_service = get_live_service()
        monitors = live_service.get_all_monitors()
        return jsonify({"success": True, "monitors": monitors})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/live/monitors", methods=["POST"])
@login_required
def add_live_monitor():
    """Add a new live monitor."""
    try:
        data = request.get_json()
        if not data or "username" not in data:
            return jsonify({"error": "Username is required"}), 400
        
        username = data["username"].strip()
        if not username:
            return jsonify({"error": "Username cannot be empty"}), 400
        
        live_service = get_live_service()
        success, message = live_service.add_monitor(username)
        
        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/live/monitors/<username>", methods=["DELETE"])
@login_required
def remove_live_monitor(username):
    """Remove a live monitor."""
    try:
        live_service = get_live_service()
        success, message = live_service.remove_monitor(username)
        
        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/live/monitors/<username>", methods=["GET"])
@login_required
def get_live_monitor_status(username):
    """Get status of a specific monitor."""
    try:
        live_service = get_live_service()
        status = live_service.get_monitor_status(username)
        
        if status:
            return jsonify({"success": True, "status": status})
        else:
            return jsonify({"error": "Monitor not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/live/settings", methods=["GET"])
@login_required
def get_live_settings():
    """Get live recording settings."""
    try:
        live_service = get_live_service()
        return jsonify({"success": True, "settings": live_service.settings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/live/settings", methods=["POST"])
@login_required
def update_live_settings():
    """Update live recording settings."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Settings data is required"}), 400
        
        live_service = get_live_service()
        success = live_service.save_settings(data)
        
        if success:
            return jsonify({"success": True, "message": "Settings updated successfully"})
        else:
            return jsonify({"error": "Failed to save settings"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/live/cli-update", methods=["POST"])
@login_required
def update_cli_tool():
    """Update the TikTok Live Recorder CLI tool."""
    try:
        live_service = get_live_service()
        success, message = live_service.update_cli_tool()
        
        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"error": message}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
