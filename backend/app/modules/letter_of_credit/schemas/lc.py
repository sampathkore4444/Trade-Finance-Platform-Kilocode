"""
Letter of Credit Schemas for Trade Finance Platform

This module defines Pydantic schemas for LC operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum


class LCTypeEnum(str, Enum):
    """LC Type enumeration."""

    IMPORT = "import"
    EXPORT = "export"
    STANDBY = "standby"
    TRANSFERABLE = "transferable"
    BACK_TO_BACK = "back_to_back"
    CONFIRMED = "confirmed"


class LCStatusEnum(str, Enum):
    """LC Status enumeration."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ISSUED = "issued"
    AMENDED = "amended"
    DOCUMENTS_RECEIVED = "documents_received"
    UNDER_EXAMINATION = "under_examination"
    PAYMENT_PROCESSED = "payment_processed"
    ACCEPTED = "accepted"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class LetterOfCreditBase(BaseModel):
    """Base Letter of Credit schema."""

    lc_type: LCTypeEnum = LCTypeEnum.IMPORT

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
    issuing_bank_address: Optional[str] = None

    # Advising Bank
    advising_bank_name: Optional[str] = None
    advising_bank_bic: Optional[str] = None

    # Amount
    currency: str = "USD"
    amount: Decimal = Field(..., gt=0)
    tolerance_percent: Decimal = Field(default=Decimal("10.00"))

    # Dates
    expiry_date: Optional[datetime] = None
    expiry_place: Optional[str] = None
    last_shipment_date: Optional[datetime] = None

    # Shipment
    shipment_from: Optional[str] = None
    shipment_to: Optional[str] = None
    partial_shipment: bool = False
    transhipment: bool = False
    shipping_terms: Optional[str] = None

    # Description
    description_goods: Optional[str] = None
    description_services: Optional[str] = None
    additional_conditions: Optional[str] = None
    documents_required: Optional[str] = None

    # Reference
    internal_reference: Optional[str] = None
    external_reference: Optional[str] = None


class LetterOfCreditCreate(LetterOfCreditBase):
    """Letter of Credit creation schema."""

    applicant_id: Optional[int] = None
    beneficiary_id: Optional[int] = None
    issuing_bank_id: Optional[int] = None
    advising_bank_id: Optional[int] = None
    confirming_bank_id: Optional[int] = None
    reimbursement_bank_id: Optional[int] = None

    is_revokable: bool = False
    is_confirmed: bool = False
    ucp_version: str = "UCP 600"
    terms_conditions: Optional[str] = None


class LetterOfCreditUpdate(BaseModel):
    """Letter of Credit update schema."""

    applicant_name: Optional[str] = None
    applicant_address: Optional[str] = None
    applicant_country: Optional[str] = None
    beneficiary_name: Optional[str] = None
    beneficiary_address: Optional[str] = None
    beneficiary_country: Optional[str] = None
    issuing_bank_name: Optional[str] = None
    issuing_bank_bic: Optional[str] = None
    issuing_bank_address: Optional[str] = None
    advising_bank_name: Optional[str] = None
    advising_bank_bic: Optional[str] = None
    currency: Optional[str] = None
    amount: Optional[Decimal] = None
    tolerance_percent: Optional[Decimal] = None
    expiry_date: Optional[datetime] = None
    expiry_place: Optional[str] = None
    last_shipment_date: Optional[datetime] = None
    shipment_from: Optional[str] = None
    shipment_to: Optional[str] = None
    partial_shipment: Optional[bool] = None
    transhipment: Optional[bool] = None
    shipping_terms: Optional[str] = None
    description_goods: Optional[str] = None
    description_services: Optional[str] = None
    additional_conditions: Optional[str] = None
    documents_required: Optional[str] = None
    internal_reference: Optional[str] = None
    external_reference: Optional[str] = None


class LetterOfCreditApprove(BaseModel):
    """LC approval schema."""

    comments: Optional[str] = None


class LetterOfCreditReject(BaseModel):
    """LC rejection schema."""

    reason: str


class LetterOfCreditResponse(LetterOfCreditBase):
    """Letter of Credit response schema."""

    id: int
    lc_number: str
    status: LCStatusEnum
    state: str
    is_revokable: bool
    is_confirmed: bool

    # Bank details
    applicant_id: Optional[int]
    beneficiary_id: Optional[int]
    issuing_bank_id: Optional[int]
    advising_bank_id: Optional[int]
    confirming_bank_id: Optional[int]
    reimbursement_bank_id: Optional[int]

    # Dates
    issue_date: Optional[datetime]
    expiry_date: Optional[datetime]
    last_shipment_date: Optional[datetime]

    # Approval
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    approval_comments: Optional[str]

    # Rejection
    rejected_by: Optional[int]
    rejected_at: Optional[datetime]
    rejection_reason: Optional[str]

    # User tracking
    created_by: Optional[int]
    assigned_to: Optional[int]

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]

    # Relationships - use computed_field to avoid lazy loading issues
    @property
    def amendments(self) -> List:
        """Return empty list for amendments relationship."""
        return []

    @property
    def documents(self) -> List:
        """Return empty list for documents relationship."""
        return []

    model_config = ConfigDict(from_attributes=True)


class LCListResponse(BaseModel):
    """LC list response schema."""

    items: List[LetterOfCreditResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
