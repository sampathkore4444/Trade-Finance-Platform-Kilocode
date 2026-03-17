"""
Risk Management Schemas Package
"""

from app.modules.risk_management.schemas.risk import (
    RiskAssessmentBase,
    RiskAssessmentResponse,
    RiskAssessmentListResponse,
    RiskLevelEnum,
)

# Aliases for backward compatibility
RiskAssessmentCreate = RiskAssessmentBase
RiskAssessmentUpdate = RiskAssessmentBase
RiskStatus = RiskLevelEnum
RiskLevel = RiskLevelEnum

__all__ = [
    "RiskAssessmentBase",
    "RiskAssessmentCreate",
    "RiskAssessmentUpdate",
    "RiskAssessmentResponse",
    "RiskAssessmentListResponse",
    "RiskLevelEnum",
    "RiskStatus",
    "RiskLevel",
]
