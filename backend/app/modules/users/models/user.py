"""
User Model for Trade Finance Platform

This module defines the User database model.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
import enum


class UserStatus(str, enum.Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    LOCKED = "locked"


# Association table for user roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
)


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Personal Information
    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(200))
    phone = Column(String(20))
    phone_country_code = Column(String(5))

    # Organization
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="SET NULL")
    )
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"))
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"))

    # Status & Security
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, index=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))

    # Login Tracking
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    last_login_at = Column(DateTime)
    last_login_ip = Column(String(45))
    password_changed_at = Column(DateTime)
    password_expires_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    # Relationships
    organization = relationship("Organization", foreign_keys=[organization_id])
    branch = relationship("Branch", foreign_keys=[branch_id])
    department = relationship("Department", foreign_keys=[department_id])
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    created_users = relationship(
        "User", back_populates="creator", foreign_keys=[created_by]
    )
    creator = relationship("User", remote_side=[id], back_populates="created_users")

    # Sessions
    sessions = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

    @property
    def permissions(self) -> list[str]:
        """Get all permissions for the user based on roles."""
        perms = set()
        for role in self.roles:
            for perm in role.permissions:
                perms.add(perm.name)
        return list(perms)
