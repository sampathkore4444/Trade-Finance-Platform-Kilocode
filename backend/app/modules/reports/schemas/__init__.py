"""
Reports Schemas Package
"""

from app.modules.reports.schemas.report import (
    ReportBase,
    ReportResponse,
    ReportTypeEnum,
)

# Aliases for backward compatibility
ReportGenerationRequest = ReportBase
ReportStatus = ReportTypeEnum
ReportType = ReportTypeEnum

__all__ = [
    "ReportBase",
    "ReportResponse",
    "ReportGenerationRequest",
    "ReportTypeEnum",
    "ReportStatus",
    "ReportType",
]
