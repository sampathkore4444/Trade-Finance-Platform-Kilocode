"""
Trade Loan Schemas Package
"""

from app.modules.trade_loan.schemas.loan import (
    TradeLoanBase,
    TradeLoanCreate,
    TradeLoanResponse,
    TradeLoanListResponse,
    LoanTypeEnum,
    LoanStatusEnum,
)

# Aliases for backward compatibility
TradeLoanUpdate = TradeLoanCreate
LoanStatus = LoanStatusEnum
LoanType = LoanTypeEnum

__all__ = [
    "TradeLoanBase",
    "TradeLoanCreate",
    "TradeLoanUpdate",
    "TradeLoanResponse",
    "TradeLoanListResponse",
    "LoanTypeEnum",
    "LoanStatusEnum",
    "LoanStatus",
    "LoanType",
]
