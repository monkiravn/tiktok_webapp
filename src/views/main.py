"""Main web interface views."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.services.auth_service import AuthService, login_required
from src.services.video_service import VideoService
from src.services.tiktok_live_service import TikTokLiveService

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Redirect to login if not authenticated, dashboard if authenticated."""
    from src.services.auth_service import AuthService

    if AuthService.is_authenticated():
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))


@bp.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard with statistics and overview."""
    return render_template("dashboard.html")


@bp.route("/video-upload", methods=["GET", "POST"])
@login_required
def video_upload():
    """Video upload page with processing functionality."""
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected", "error")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No file selected", "error")
            return redirect(request.url)

        try:
            video_service = VideoService()
            result = video_service.process_upload(file)
            flash("Video processed successfully!", "success")
            return render_template("video_upload.html", result=result)
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            return redirect(request.url)

    return render_template("video_upload.html")


@bp.route("/tiktok-live", methods=["GET", "POST"])
@login_required
def tiktok_live():
    """TikTok Live Monitoring page."""
    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        if user_input:
            try:
                tiktok_service = TikTokLiveService()
                success, message = tiktok_service.add_user_to_monitor(user_input)
                if success:
                    flash(message, "success")
                else:
                    flash(message, "error")
            except Exception as e:
                flash(f"Error: {str(e)}", "error")
        else:
            flash("Please enter a TikTok username or URL", "error")
        return redirect(request.url)

    # Get monitored users for display
    try:
        tiktok_service = TikTokLiveService()
        monitored_users = tiktok_service.get_monitored_users()
    except Exception as e:
        monitored_users = []
        flash(f"Error loading monitored users: {str(e)}", "error")

    return render_template("tiktok_live.html", monitored_users=monitored_users)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("login.html")

        if AuthService.login(username, password):
            # Redirect to the originally requested page or dashboard
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("main.dashboard"))
        else:
            flash("Invalid username or password.", "error")
            return render_template("login.html")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    """Logout page."""
    AuthService.logout()
    return redirect(url_for("main.index"))
