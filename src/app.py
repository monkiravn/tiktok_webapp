"""Flask application factory and configuration."""

import os

from flask import Flask

from src.config import get_config
from src.extensions import init_extensions


def create_app(config_name=None):
    """Create and configure Flask application."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    # Load configuration
    config = get_config(config_name)
    app.config.update(config.to_dict())

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    from src.views.api import bp as api_bp
    from src.views.main import bp as main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api/v1")


def register_error_handlers(app):
    """Register error handlers."""

    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500

    @app.errorhandler(413)
    def too_large(error):
        return {"error": "File too large"}, 413
