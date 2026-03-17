"""
Risk Management Schemas
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from enum import Enum


class RiskLevelEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAssessmentBase(BaseModel):
    entity_type: str
    entity_id: int
    risk_type: str
    risk_level: RiskLevelEnum
    score: Optional[Decimal] = None
    findings: Optional[str] = None
    recommendations: Optional[str] = None


class RiskAssessmentResponse(RiskAssessmentBase):
    id: int
    assessment_date: datetime
    expiry_date: Optional[datetime]
    assessed_by: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RiskAssessmentListResponse(BaseModel):
    items: List[RiskAssessmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
