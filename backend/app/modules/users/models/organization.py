"""
Organization Model for Trade Finance Platform
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Organization(Base):
    """Organization model for multi-tenant support."""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(20), unique=True, nullable=False, index=True)
    registration_number = Column(String(50))
    tax_id = Column(String(50))
    address = Column(String(500))
    city = Column(String(100))
    country = Column(String(100))
    phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))

    # Banking Details
    bank_name = Column(String(255))
    bank_account = Column(String(50))
    bank_account_name = Column(String(255))
    swift_code = Column(String(20))

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    branches = relationship(
        "Branch", back_populates="organization", cascade="all, delete-orphan"
    )
    users = relationship("User", back_populates="organization")


class Branch(Base):
    """Branch model for organization branches."""

    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    code = Column(String(20))
    address = Column(String(500))
    city = Column(String(100))
    country = Column(String(100))
    phone = Column(String(20))
    email = Column(String(255))
    swift_code = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="branches")
    users = relationship("User", back_populates="branch")


class Department(Base):
    """Department model for organization departments."""

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    code = Column(String(20))
    description = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="department")
