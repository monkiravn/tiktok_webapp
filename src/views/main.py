"""Main web interface views."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.services.auth_service import AuthService, login_required
from src.services.video_service import VideoService

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Redirect to login if not authenticated, dashboard if authenticated."""
    from src.services.auth_service import AuthService

    if AuthService.is_authenticated():
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))


@bp.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    """Main dashboard with video upload functionality."""
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
            return render_template("result.html", result=result)
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            return redirect(request.url)

    return render_template("dashboard.html")


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
