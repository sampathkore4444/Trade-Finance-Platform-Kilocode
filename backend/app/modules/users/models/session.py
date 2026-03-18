"""
User Session Model for Trade Finance Platform
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class UserSession(Base):
    """User session model for tracking active sessions."""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token = Column(String(2000), unique=True, nullable=False, index=True)
    refresh_token = Column(String(2000), unique=True, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    device_info = Column(String(255))
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    last_activity_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")
