"""
Permission Model for Trade Finance Platform
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Permission(Base):
    """Permission model for RBAC."""

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255))
    resource = Column(String(50))
    action = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    roles = relationship(
        "Role", secondary="role_permissions", back_populates="permissions"
    )
