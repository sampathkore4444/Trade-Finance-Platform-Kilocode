"""
Reports Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum


class ReportType(str, Enum):
    LC_SUMMARY = "lc_summary"
    GUARANTEE_SUMMARY = "guarantee_summary"
    LOAN_SUMMARY = "loan_summary"
    PORTFOLIO_SUMMARY = "portfolio_summary"
    COMPLIANCE = "compliance"


class ReportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportBase(BaseModel):
    report_type: ReportType
    title: Optional[str] = None
    description: Optional[str] = None


class ReportGenerationRequest(BaseModel):
    report_type: ReportType
    title: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[dict] = None


class ReportResponse(ReportBase):
    id: int
    report_number: str
    status: ReportStatus
    file_path: Optional[str]
    filename: Optional[str]
    generated_by: Optional[int]
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
