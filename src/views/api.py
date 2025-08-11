"""API views for REST endpoints."""

from flask import Blueprint, jsonify, request, send_file, current_app
import os

from src.services.video_service import VideoService
from src.services.auth_service import login_required
from src.services.tiktok_live_service import TikTokLiveService

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

@bp.route("/tiktok-live/add-user", methods=["POST"])
@login_required
def add_user_to_monitor():
    """Add a TikTok user to monitoring list."""
    try:
        data = request.get_json()
        if not data or "user_input" not in data:
            return jsonify({"error": "user_input is required"}), 400

        user_input = data["user_input"].strip()
        if not user_input:
            return jsonify({"error": "user_input cannot be empty"}), 400

        tiktok_service = TikTokLiveService()
        success, message = tiktok_service.add_user_to_monitor(user_input)

        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": message}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/tiktok-live/remove-user", methods=["POST"])
@login_required
def remove_user_from_monitor():
    """Remove a TikTok user from monitoring list."""
    try:
        data = request.get_json()
        if not data or "username" not in data:
            return jsonify({"error": "username is required"}), 400

        username = data["username"].strip().replace('@', '')
        if not username:
            return jsonify({"error": "username cannot be empty"}), 400

        tiktok_service = TikTokLiveService()
        success, message = tiktok_service.remove_user_from_monitor(username)

        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": message}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/tiktok-live/monitored-users", methods=["GET"])
@login_required
def get_monitored_users():
    """Get list of monitored TikTok users."""
    try:
        tiktok_service = TikTokLiveService()
        users = tiktok_service.get_monitored_users()
        return jsonify({"success": True, "users": users})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/tiktok-live/start-monitoring", methods=["POST"])
@login_required
def start_monitoring():
    """Start TikTok live monitoring."""
    try:
        tiktok_service = TikTokLiveService()
        tiktok_service.start_monitoring()
        return jsonify({"success": True, "message": "Monitoring started"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/tiktok-live/stop-monitoring", methods=["POST"])
@login_required
def stop_monitoring():
    """Stop TikTok live monitoring."""
    try:
        tiktok_service = TikTokLiveService()
        tiktok_service.stop_monitoring()
        return jsonify({"success": True, "message": "Monitoring stopped"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/tiktok-live/get-settings", methods=["GET"])
@login_required
def get_tiktok_settings():
    """Get TikTok live monitoring settings."""
    try:
        from flask import current_app
        
        settings = {
            "recording_duration": current_app.config.get('TIKTOK_RECORDING_DURATION', 0),
            "check_interval": current_app.config.get('TIKTOK_CHECK_INTERVAL', 60),
            "monitoring_enabled": current_app.config.get('TIKTOK_MONITORING_ENABLED', True)
        }
        
        return jsonify({"success": True, "settings": settings})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/tiktok-live/update-settings", methods=["POST"])
@login_required  
def update_tiktok_settings():
    """Update TikTok live monitoring settings."""
    try:
        from flask import current_app, request
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update recording duration if provided
        if 'recording_duration' in data:
            duration = int(data['recording_duration'])
            if duration < 0:
                return jsonify({"error": "Recording duration must be non-negative"}), 400
            current_app.config['TIKTOK_RECORDING_DURATION'] = duration
        
        # Update check interval if provided
        if 'check_interval' in data:
            interval = int(data['check_interval'])
            if interval < 30:
                return jsonify({"error": "Check interval must be at least 30 seconds"}), 400
            current_app.config['TIKTOK_CHECK_INTERVAL'] = interval
        
        return jsonify({"success": True, "message": "Settings updated successfully"})

    except ValueError:
        return jsonify({"error": "Invalid numeric value provided"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/tiktok-live/get-cookies", methods=["GET"])
@protected
def get_tiktok_cookies():
    """Get current TikTok cookies configuration"""
    try:
        tiktok_service = TikTokLiveService()
        cookies = tiktok_service.get_cookies()
        
        return jsonify({
            "success": True,
            "cookies": cookies
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/tiktok-live/update-cookies", methods=["POST"])
@protected
def update_tiktok_cookies():
    """Update TikTok cookies configuration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        cookies = data.get('cookies', {})
        if not isinstance(cookies, dict):
            return jsonify({"error": "Cookies must be a dictionary"}), 400
        
        tiktok_service = TikTokLiveService()
        success = tiktok_service.update_cookies(cookies)
        
        if success:
            return jsonify({
                "success": True, 
                "message": "Cookies updated successfully"
            })
        else:
            return jsonify({"error": "Failed to update cookies"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/tiktok-live/reload-cookies", methods=["POST"])
@protected
def reload_tiktok_cookies():
    """Reload TikTok cookies from configuration file"""
    try:
        tiktok_service = TikTokLiveService()
        success = tiktok_service.reload_cookies()
        
        if success:
            return jsonify({
                "success": True, 
                "message": "Cookies reloaded successfully"
            })
        else:
            return jsonify({"error": "Failed to reload cookies"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
