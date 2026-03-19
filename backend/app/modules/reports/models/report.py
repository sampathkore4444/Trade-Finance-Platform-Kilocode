"""
Reports Models
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base
import enum


class ReportType(str, enum.Enum):
    LC_SUMMARY = "lc_summary"
    GUARANTEE_SUMMARY = "guarantee_summary"
    LOAN_SUMMARY = "loan_summary"
    PORTFOLIO_SUMMARY = "portfolio_summary"
    COMPLIANCE = "compliance"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(String(50), unique=True)
    report_type = Column(
        Enum(ReportType, values_callable=lambda x: [e.value for e in ReportType])
    )
    title = Column(String(255))
    description = Column(Text)
    status = Column(
        Enum(ReportStatus, values_callable=lambda x: [e.value for e in ReportStatus]),
        default=ReportStatus.PENDING,
    )
    file_path = Column(String(500))
    filename = Column(String(255))
    parameters = Column(Text)  # JSON string
    generated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    generated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, server_default=func.now())
