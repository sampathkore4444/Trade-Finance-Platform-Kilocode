"""
Auth Session Model for Trade Finance Platform
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base


class AuthSession(Base):
    """Authentication session model for tracking user sessions."""

    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    session_token = Column(String(500), unique=True, index=True)
    refresh_token = Column(String(500), unique=True, index=True)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<AuthSession(id={self.id}, user_id={self.user_id})>"
