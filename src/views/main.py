"""Main web interface views."""

from flask import Blueprint, flash, redirect, render_template, request

from src.services.video_service import VideoService

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Home page."""
    return render_template("index.html")


@bp.route("/upload", methods=["GET", "POST"])
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
