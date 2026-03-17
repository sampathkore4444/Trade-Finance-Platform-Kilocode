"""
Trade Loan Model for Trade Finance Platform
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    Numeric,
)
from sqlalchemy.sql import func
from app.database import Base
import enum


class LoanType(str, enum.Enum):
    IMPORT_LOAN = "import_loan"
    EXPORT_LOAN = "export_loan"
    WORKING_CAPITAL = "working_capital"
    STRUCTURED_FINANCE = "structured_finance"


class LoanStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISBURSED = "disbursed"
    REPAID = "repaid"
    DEFAULTED = "defaulted"
    CANCELLED = "cancelled"


class TradeLoan(Base):
    __tablename__ = "trade_loans"

    id = Column(Integer, primary_key=True, index=True)
    loan_number = Column(String(50), unique=True, nullable=False, index=True)
    loan_type = Column(Enum(LoanType), nullable=False)
    status = Column(Enum(LoanStatus), default=LoanStatus.DRAFT)

    borrower_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))
    borrower_name = Column(String(255))

    currency = Column(String(3), default="USD")
    principal_amount = Column(Numeric(18, 2), nullable=False)
    interest_rate = Column(Numeric(8, 4))
    disbursed_amount = Column(Numeric(18, 2))
    outstanding_amount = Column(Numeric(18, 2))

    start_date = Column(DateTime)
    end_date = Column(DateTime)

    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<TradeLoan(id={self.id}, loan_number='{self.loan_number}')>"
