"""Database initialization and seeding utilities."""

import os
from flask import current_app

from src.models.user import db
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
        # Create admin user with admin role and approved status
        UserRepository.create_user(admin_username, admin_password, role='admin', status='approved')
        current_app.logger.info(f"Admin user '{admin_username}' created successfully")
    else:
        # Update existing user to admin role and approved status if needed
        if existing_user.role != 'admin' or existing_user.status != 'approved':
            existing_user.role = 'admin'
            existing_user.status = 'approved'
            from src.models.user import db
            db.session.commit()
            current_app.logger.info(f"Admin user '{admin_username}' updated to admin role and approved status")
        else:
            current_app.logger.info(f"Admin user '{admin_username}' already exists")


def setup_database() -> None:
    """Complete database setup including initialization and seeding."""
    init_database()
    seed_admin_user()