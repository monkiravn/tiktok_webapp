"""Main web interface views."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from src.services.auth_service import AuthService, login_required, admin_required
from src.services.video_service import VideoService
from src.repositories.user_repository import UserRepository

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


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("login.html")

        # Check if user exists and credentials are valid
        user = UserRepository.get_by_username(username)
        if user and user.check_password(password):
            if not user.is_approved():
                flash("Your account is pending admin approval. Please contact an administrator.", "warning")
                return render_template("login.html")
            
            # Login the user
            if AuthService.login(username, password):
                # Redirect to the originally requested page or dashboard
                next_page = request.args.get("next")
                if next_page:
                    return redirect(next_page)
                return redirect(url_for("main.dashboard"))
        
        flash("Invalid username or password.", "error")
        return render_template("login.html")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    """Logout page."""
    AuthService.logout()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Registration page for new users."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        # Validation
        if not username or not password or not confirm_password:
            flash("Please fill in all fields.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("register.html")

        # Check if username already exists
        existing_user = UserRepository.get_by_username(username)
        if existing_user:
            flash("Username already exists. Please choose a different one.", "error")
            return render_template("register.html")

        try:
            # Create new user with pending status
            UserRepository.create_user(username, password, role='user', status='pending')
            flash("Registration successful! Your account is pending admin approval. You will be notified once approved.", "success")
            return redirect(url_for("main.login"))
        except Exception as e:
            flash("An error occurred during registration. Please try again.", "error")
            return render_template("register.html")

    return render_template("register.html")


@bp.route("/admin/users")
@admin_required
def admin_users():
    """Admin page to manage user approvals."""
    pending_users = UserRepository.get_pending_users()
    all_users = UserRepository.get_all_users()
    return render_template("admin_users.html", pending_users=pending_users, all_users=all_users)


@bp.route("/admin/approve_user/<int:user_id>", methods=["POST"])
@admin_required
def approve_user(user_id):
    """Approve a pending user."""
    user = UserRepository.get_by_id(user_id)
    if user and user.status == 'pending':
        UserRepository.approve_user(user)
        flash(f"User '{user.username}' has been approved.", "success")
    else:
        flash("User not found or already approved.", "error")
    
    return redirect(url_for("main.admin_users"))
