"""
Risk Management Services Package
"""

from app.modules.risk_management.services.risk_service import (
    risk_service,
    RiskManagementService,
)

__all__ = ["risk_service", "RiskManagementService"]
