"""
Compliance Schemas Package
"""

from app.modules.compliance.schemas.compliance import (
    ComplianceCheckBase,
    ComplianceCheckResponse,
    ComplianceStatusEnum,
)

# Aliases for backward compatibility
ComplianceCheckCreate = ComplianceCheckBase
ComplianceCheckUpdate = ComplianceCheckBase
ComplianceStatus = ComplianceStatusEnum
ComplianceType = ComplianceStatusEnum

__all__ = [
    "ComplianceCheckBase",
    "ComplianceCheckCreate",
    "ComplianceCheckUpdate",
    "ComplianceCheckResponse",
    "ComplianceStatusEnum",
    "ComplianceStatus",
    "ComplianceType",
]
