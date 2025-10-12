"""
Database models for Brody application
"""
import os
import uuid
from datetime import datetime
from typing import Optional

try:
    from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.sql import func
    from database import Base
except ImportError:
    # Graceful degradation if SQLAlchemy not installed
    Column = String = DateTime = Boolean = Text = JSON = UUID = func = None
    Base = object

def generate_uuid():
    return str(uuid.uuid4())

class User(Base if Base != object else object):
    """User model with authentication and preferences"""
    __tablename__ = "users"

    if Column:  # Only define table if SQLAlchemy is available
        id = Column(String, primary_key=True, default=generate_uuid)
        email = Column(String(255), unique=True, index=True, nullable=False)
        name = Column(String(255), nullable=False)
        password_hash = Column(String(255))
        is_active = Column(Boolean, default=True)
        is_verified = Column(Boolean, default=False)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), onupdate=func.now())
        last_login = Column(DateTime(timezone=True))
        
        # User preferences stored as JSON
        preferences = Column(JSON, default=dict)
        
        # Encrypted API keys and integration tokens
        api_keys = Column(JSON, default=dict)  # Will be encrypted
        
        # OAuth provider info
        oauth_provider = Column(String(50))  # 'google', 'microsoft', etc.
        oauth_id = Column(String(255))

class EmailAccount(Base if Base != object else object):
    """Email account integrations for users"""
    __tablename__ = "email_accounts"

    if Column:
        id = Column(String, primary_key=True, default=generate_uuid)
        user_id = Column(String, nullable=False, index=True)
        provider = Column(String(50), nullable=False)  # 'gmail', 'outlook'
        email_address = Column(String(255), nullable=False)
        
        # Encrypted tokens
        access_token = Column(Text)  # Will be encrypted
        refresh_token = Column(Text)  # Will be encrypted
        
        last_sync = Column(DateTime(timezone=True))
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserSession(Base if Base != object else object):
    """User session tracking"""
    __tablename__ = "user_sessions"

    if Column:
        id = Column(String, primary_key=True, default=generate_uuid)
        user_id = Column(String, nullable=False, index=True)
        session_token = Column(String(255), unique=True, nullable=False)
        expires_at = Column(DateTime(timezone=True), nullable=False)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        last_activity = Column(DateTime(timezone=True), server_default=func.now())
        
        # Session metadata
        ip_address = Column(String(45))  # IPv6 compatible
        user_agent = Column(Text)
        is_active = Column(Boolean, default=True)