"""
Compliance Models
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base
import enum


class ComplianceStatus(str, enum.Enum):
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    REVIEW_REQUIRED = "review_required"


class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    check_type = Column(String(100))  # KYC, AML, SANCTIONS
    status = Column(Enum(ComplianceStatus), default=ComplianceStatus.PENDING)
    check_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)
    findings = Column(Text)
    checked_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())
