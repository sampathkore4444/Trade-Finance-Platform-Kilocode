"""
Risk Management Models
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    Numeric,
)
from sqlalchemy.sql import func
from app.database import Base
import enum


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50))  # organization, lc, guarantee, etc.
    entity_id = Column(Integer)
    risk_type = Column(String(100))  # credit, market, operational
    risk_level = Column(Enum(RiskLevel))
    score = Column(Numeric(5, 2))
    assessment_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime)
    findings = Column(Text)
    recommendations = Column(Text)
    assessed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<RiskAssessment(id={self.id}, level={self.risk_level})>"
