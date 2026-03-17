"""
Reports Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum


class ReportTypeEnum(str, Enum):
    LC_REPORT = "lc_report"
    GUARANTEE_REPORT = "guarantee_report"
    LOAN_REPORT = "loan_report"
    COMPLIANCE_REPORT = "compliance_report"
    RISK_REPORT = "risk_report"


class ReportBase(BaseModel):
    report_type: ReportTypeEnum
    title: Optional[str] = None
    description: Optional[str] = None


class ReportResponse(ReportBase):
    id: int
    report_number: str
    file_path: Optional[str]
    file_name: Optional[str]
    generated_by: Optional[int]
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
