"""
Trade Loan Schemas
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class LoanTypeEnum(str, Enum):
    IMPORT_LOAN = "import_loan"
    EXPORT_LOAN = "export_loan"
    WORKING_CAPITAL = "working_capital"
    STRUCTURED_FINANCE = "structured_finance"


class LoanStatusEnum(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISBURSED = "disbursed"
    REPAID = "repaid"
    DEFAULTED = "defaulted"
    CANCELLED = "cancelled"


class TradeLoanBase(BaseModel):
    loan_type: LoanTypeEnum
    borrower_name: Optional[str] = None
    currency: str = "USD"
    principal_amount: Decimal = Field(..., gt=0)
    interest_rate: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class TradeLoanCreate(TradeLoanBase):
    borrower_id: Optional[int] = None


class TradeLoanResponse(TradeLoanBase):
    id: int
    loan_number: str
    status: LoanStatusEnum
    borrower_id: Optional[int]
    disbursed_amount: Optional[Decimal]
    outstanding_amount: Optional[Decimal]
    created_by: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TradeLoanListResponse(BaseModel):
    items: List[TradeLoanResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
