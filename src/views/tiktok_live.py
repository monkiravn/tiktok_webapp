"""TikTok Live Monitoring routes"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for

from src.services.auth_service import login_required
from src.services.tiktok_live_service import tiktok_service

bp = Blueprint("tiktok_live", __name__, url_prefix="/live")


@bp.route("/")
@login_required
def live_monitoring():
    """TikTok live monitoring dashboard"""
    status = tiktok_service.get_monitoring_status()
    settings = tiktok_service.get_settings()
    return render_template("live_monitoring.html", status=status, settings=settings)


@bp.route("/api/status")
@login_required
def api_status():
    """Get monitoring status via API"""
    return jsonify(tiktok_service.get_monitoring_status())


@bp.route("/api/start", methods=["POST"])
@login_required
def api_start():
    """Start monitoring"""
    try:
        success = tiktok_service.start_monitoring()
        return jsonify({"success": success, "message": "Monitoring started" if success else "Monitoring already running"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@bp.route("/api/stop", methods=["POST"])
@login_required
def api_stop():
    """Stop monitoring"""
    try:
        tiktok_service.stop_monitoring()
        return jsonify({"success": True, "message": "Monitoring stopped"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@bp.route("/api/users", methods=["GET"])
@login_required
def api_get_users():
    """Get all monitored users"""
    status = tiktok_service.get_monitoring_status()
    return jsonify(status["users"])


@bp.route("/api/users", methods=["POST"])
@login_required
def api_add_user():
    """Add a user to monitoring"""
    try:
        data = request.get_json()
        if not data or "username" not in data:
            return jsonify({"success": False, "message": "Username is required"}), 400
        
        username = data["username"].strip()
        if not username:
            return jsonify({"success": False, "message": "Username cannot be empty"}), 400
        
        user_id = tiktok_service.add_user(username)
        return jsonify({
            "success": True, 
            "message": f"User @{username} added to monitoring",
            "user_id": user_id
        })
        
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error adding user: {str(e)}"}), 500


@bp.route("/api/users/<user_id>", methods=["DELETE"])
@login_required
def api_remove_user(user_id):
    """Remove a user from monitoring"""
    try:
        success = tiktok_service.remove_user(user_id)
        if success:
            return jsonify({"success": True, "message": "User removed from monitoring"})
        else:
            return jsonify({"success": False, "message": "User not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@bp.route("/api/settings", methods=["GET"])
@login_required  
def api_get_settings():
    """Get monitoring settings"""
    return jsonify(tiktok_service.get_settings())


@bp.route("/api/settings", methods=["POST"])
@login_required
def api_update_settings():
    """Update monitoring settings"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Settings data is required"}), 400
        
        tiktok_service.update_settings(data)
        return jsonify({"success": True, "message": "Settings updated successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@bp.route("/settings")
@login_required
def settings():
    """Settings page for TikTok live monitoring"""
    current_settings = tiktok_service.get_settings()
    return render_template("live_settings.html", settings=current_settings)


@bp.route("/settings", methods=["POST"])
@login_required
def update_settings():
    """Update settings via form"""
    try:
        settings_data = {
            "check_interval": int(request.form.get("check_interval", 2)),
            "recording_duration": int(request.form.get("recording_duration")) if request.form.get("recording_duration") else None,
            "output_directory": request.form.get("output_directory", "recordings"),
            "telegram_enabled": bool(request.form.get("telegram_enabled")),
            "telegram_bot_token": request.form.get("telegram_bot_token", ""),
            "telegram_chat_id": request.form.get("telegram_chat_id", "")
        }
        
        tiktok_service.update_settings(settings_data)
        flash("Settings updated successfully!", "success")
        
    except ValueError as e:
        flash(f"Invalid settings: {str(e)}", "error")
    except Exception as e:
        flash(f"Error updating settings: {str(e)}", "error")
    
    return redirect(url_for("tiktok_live.settings"))