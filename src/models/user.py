"""User model for authentication."""

import bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Create database instance
db = SQLAlchemy()

# Create base model class
Base = declarative_base()


class User(db.Model):
    """User model for storing user credentials."""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False, default='user')  # 'admin' or 'user'
    status = Column(String(20), nullable=False, default='pending')  # 'approved' or 'pending'
    
    def __init__(self, username: str, password: str, role: str = 'user', status: str = 'pending'):
        """Initialize user with username, hashed password, role and status."""
        self.username = username
        self.role = role
        self.status = status
        self.set_password(password)
    
    def set_password(self, password: str) -> None:
        """Hash and set password."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches the stored hash."""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == 'admin'
    
    def is_approved(self) -> bool:
        """Check if user is approved."""
        return self.status == 'approved'
    
    def approve(self) -> None:
        """Approve the user account."""
        self.status = 'approved'
    
    def __repr__(self):
        """String representation of user."""
        return f'<User {self.username}>'