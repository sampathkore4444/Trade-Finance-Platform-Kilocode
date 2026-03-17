"""
Trade Loan Services Package
"""

from app.modules.trade_loan.services.loan_service import (
    trade_loan_service,
    TradeLoanService,
)

__all__ = [
    "trade_loan_service",
    "TradeLoanService",
]
