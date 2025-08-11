"""Database initialization and seeding utilities."""

import os
from flask import current_app

from src.models.user import db
from src.models.tiktok_models import MonitoredUser, LiveRecording
from src.repositories.user_repository import UserRepository


def init_database() -> None:
    """Initialize the database by creating all tables."""
    db.create_all()
    current_app.logger.info("Database tables created successfully")


def seed_admin_user() -> None:
    """Seed the database with the default admin user if it doesn't exist."""
    # Get admin credentials from configuration
    admin_username = current_app.config.get('ADMIN_USERNAME', 'admin')
    admin_password = current_app.config.get('ADMIN_PASSWORD', 'password123')
    
    # Check if admin user already exists
    existing_user = UserRepository.get_by_username(admin_username)
    if existing_user is None:
        # Create admin user
        UserRepository.create_user(admin_username, admin_password)
        current_app.logger.info(f"Admin user '{admin_username}' created successfully")
    else:
        current_app.logger.info(f"Admin user '{admin_username}' already exists")


def setup_database() -> None:
    """Complete database setup including initialization and seeding."""
    init_database()
    seed_admin_user()