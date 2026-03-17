"""
Reports Models
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base
import enum


class ReportType(str, enum.Enum):
    LC_REPORT = "lc_report"
    GUARANTEE_REPORT = "guarantee_report"
    LOAN_REPORT = "loan_report"
    COMPLIANCE_REPORT = "compliance_report"
    RISK_REPORT = "risk_report"


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(String(50), unique=True)
    report_type = Column(Enum(ReportType))
    title = Column(String(255))
    description = Column(Text)
    file_path = Column(String(500))
    file_name = Column(String(255))
    parameters = Column(Text)  # JSON string
    generated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    generated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, server_default=func.now())
