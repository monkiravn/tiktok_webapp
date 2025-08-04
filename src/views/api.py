"""API views for REST endpoints."""

from flask import Blueprint, jsonify, request

from src.services.video_service import VideoService

bp = Blueprint("api", __name__)


@bp.route("/health")
def health():
    """Health check endpoint."""
    return jsonify(
        {"status": "healthy", "service": "tiktok-reup-webapp", "version": "1.0.0"}
    )


@bp.route("/upload", methods=["POST"])
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
