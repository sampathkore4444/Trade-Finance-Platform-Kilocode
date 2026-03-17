"""
Compliance Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from enum import Enum


class ComplianceStatusEnum(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    REVIEW_REQUIRED = "review_required"


class ComplianceCheckBase(BaseModel):
    entity_type: str
    entity_id: int
    check_type: str
    findings: Optional[str] = None


class ComplianceCheckResponse(ComplianceCheckBase):
    id: int
    status: ComplianceStatusEnum
    check_date: datetime
    expiry_date: Optional[datetime]
    checked_by: Optional[int]

    model_config = ConfigDict(from_attributes=True)
