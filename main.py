#!/usr/bin/env python3
"""
TikTok Re-Upload WebApp - Main Entry Point
"""

from src.app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    app_config = app.config
    host = app_config.get("HOST", "0.0.0.0")
    port = app_config.get("PORT", 5000)
    debug = app_config.get("DEBUG", False)

    app.run(host=host, port=port, debug=debug)
