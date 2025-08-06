"""Main web interface views."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.services.video_service import VideoService
from src.services.auth_service import AuthService, login_required

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Home page."""
    return render_template("index.html")


@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Video upload page."""
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

    return render_template("upload.html")


@bp.route("/about")
def about():
    """About page."""
    return render_template("about.html")


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
            flash("Login successful!", "success")
            # Redirect to the originally requested page or upload page
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.upload'))
        else:
            flash("Invalid username or password.", "error")
            return render_template("login.html")
    
    return render_template("login.html")


@bp.route("/logout")
def logout():
    """Logout page."""
    AuthService.logout()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('main.index'))
