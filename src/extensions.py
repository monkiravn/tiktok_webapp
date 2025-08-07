"""Flask extensions initialization."""

from datetime import datetime

from src.models.user import db


def init_extensions(app):
    """Initialize Flask extensions."""
    # Set SQLAlchemy database URI before initializing
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get('DATABASE_URL')
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Register custom template filters
    register_template_filters(app)
    
    # Initialize database tables and seed admin user (only in non-testing environments)
    with app.app_context():
        from src.database import init_database, seed_admin_user
        init_database()
        if not app.config.get('TESTING', False):
            seed_admin_user()


def register_template_filters(app):
    """Register custom template filters."""

    @app.template_filter("datetimeformat")
    def datetimeformat(value, format="%B %d, %Y at %I:%M %p"):
        """Format a datetime object for display."""
        if value is None:
            return ""

        # If value is a string, try to parse it as datetime
        if isinstance(value, str):
            try:
                # Try different datetime formats
                for fmt in [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M:%S.%f",
                    "%Y-%m-%dT%H:%M:%S",
                ]:
                    try:
                        value = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # If no format works, return the original string
                    return value
            except (ValueError, TypeError):
                return value

        # If value is datetime object, format it
        if isinstance(value, datetime):
            return value.strftime(format)

        return str(value)
