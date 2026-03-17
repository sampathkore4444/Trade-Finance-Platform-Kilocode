"""
Bank Guarantee Schemas for Trade Finance Platform

This module defines Pydantic schemas for Bank Guarantee operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class GuaranteeTypeEnum(str, Enum):
    """Guarantee Type enumeration."""

    BID_BOND = "bid_bond"
    PERFORMANCE_BOND = "performance_bond"
    ADVANCE_PAYMENT_GUARANTEE = "advance_payment_guarantee"
    PAYMENT_GUARANTEE = "payment_guarantee"
    WARRANTY_GUARANTEE = "warranty_guarantee"
    CUSTOMS_GUARANTEE = "customs_guarantee"
    JUDICIAL_GUARANTEE = "judicial_guarantee"
    FINANCIAL_GUARANTEE = "financial_guarantee"


class GuaranteeStatusEnum(str, Enum):
    """Guarantee Status enumeration."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ISSUED = "issued"
    ACTIVE = "active"
    EXPIRED = "expired"
    CLAIMED = "claimed"
    RELEASED = "released"
    CANCELLED = "cancelled"


class BankGuaranteeBase(BaseModel):
    """Base Bank Guarantee schema."""

    guarantee_type: GuaranteeTypeEnum

    # Applicant
    applicant_name: Optional[str] = None
    applicant_address: Optional[str] = None
    applicant_country: Optional[str] = None

    # Beneficiary
    beneficiary_name: Optional[str] = None
    beneficiary_address: Optional[str] = None
    beneficiary_country: Optional[str] = None

    # Issuing Bank
    issuing_bank_name: Optional[str] = None
    issuing_bank_bic: Optional[str] = None

    # Amount
    currency: str = "USD"
    amount: Decimal = Field(..., gt=0)

    # Dates
    expiry_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None

    # Terms
    guarantee_terms: Optional[str] = None
    claim_conditions: Optional[str] = None
    undertaking_type: Optional[str] = None
    is_revokable: bool = False

    # Auto-renewal
    is_auto_renewal: bool = False
    renewal_period_days: Optional[int] = None
    renewal_notice_days: Optional[int] = None

    # Reference
    internal_reference: Optional[str] = None
    external_reference: Optional[str] = None
    related_contract_id: Optional[str] = None


class BankGuaranteeCreate(BankGuaranteeBase):
    """Bank Guarantee creation schema."""

    applicant_id: Optional[int] = None
    beneficiary_id: Optional[int] = None
    issuing_bank_id: Optional[int] = None
    related_lc_id: Optional[int] = None


class BankGuaranteeUpdate(BaseModel):
    """Bank Guarantee update schema."""

    applicant_name: Optional[str] = None
    applicant_address: Optional[str] = None
    applicant_country: Optional[str] = None
    beneficiary_name: Optional[str] = None
    beneficiary_address: Optional[str] = None
    beneficiary_country: Optional[str] = None
    issuing_bank_name: Optional[str] = None
    issuing_bank_bic: Optional[str] = None
    currency: Optional[str] = None
    amount: Optional[Decimal] = None
    expiry_date: Optional[datetime] = None
    effective_date: Optional[datetime] = None
    guarantee_terms: Optional[str] = None
    claim_conditions: Optional[str] = None
    undertaking_type: Optional[str] = None
    is_revokable: Optional[bool] = None
    is_auto_renewal: Optional[bool] = None
    renewal_period_days: Optional[int] = None
    renewal_notice_days: Optional[int] = None
    internal_reference: Optional[str] = None
    external_reference: Optional[str] = None
    related_contract_id: Optional[str] = None


class BankGuaranteeApprove(BaseModel):
    """Guarantee approval schema."""

    comments: Optional[str] = None


class BankGuaranteeReject(BaseModel):
    """Guarantee rejection schema."""

    reason: str


class BankGuaranteeClaim(BaseModel):
    """Guarantee claim schema."""

    claim_amount: Decimal
    claim_reason: str


class BankGuaranteeRelease(BaseModel):
    """Guarantee release schema."""

    release_amount: Optional[Decimal] = None
    release_reason: Optional[str] = None


class BankGuaranteeResponse(BankGuaranteeBase):
    """Bank Guarantee response schema."""

    id: int
    guarantee_number: str
    status: GuaranteeStatusEnum
    state: str
    is_revokable: bool
    is_auto_renewal: bool

    # Bank details
    applicant_id: Optional[int]
    beneficiary_id: Optional[int]
    issuing_bank_id: Optional[int]

    # Dates
    issue_date: Optional[datetime]
    effective_date: Optional[datetime]
    expiry_date: Optional[datetime]

    # Approval
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    approval_comments: Optional[str]

    # Rejection
    rejected_by: Optional[int]
    rejected_at: Optional[datetime]
    rejection_reason: Optional[str]

    # Claim
    claimed_by: Optional[int]
    claimed_at: Optional[datetime]
    claim_amount: Optional[Decimal]
    claim_status: Optional[str]

    # Release
    released_by: Optional[int]
    released_at: Optional[datetime]
    release_amount: Optional[Decimal]

    # References
    related_lc_id: Optional[int]

    # User tracking
    created_by: Optional[int]
    assigned_to: Optional[int]

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class GuaranteeListResponse(BaseModel):
    """Guarantee list response schema."""

    items: List[BankGuaranteeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
