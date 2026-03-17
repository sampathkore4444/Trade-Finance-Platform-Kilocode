"""
Bank Guarantee Model for Trade Finance Platform

This module defines the Bank Guarantee database model.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    Numeric,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
import enum


class GuaranteeType(str, enum.Enum):
    """
    Bank Guarantee types.
    """

    BID_BOND = "bid_bond"
    PERFORMANCE_BOND = "performance_bond"
    ADVANCE_PAYMENT_GUARANTEE = "advance_payment_guarantee"
    PAYMENT_GUARANTEE = "payment_guarantee"
    WARRANTY_GUARANTEE = "warranty_guarantee"
    customs_GUARANTEE = "customs_guarantee"
    JUDICIAL_GUARANTEE = "judicial_guarantee"
    FINANCIAL_GUARANTEE = "financial_guarantee"


class GuaranteeStatus(str, enum.Enum):
    """
    Bank Guarantee status.
    """

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


class GuaranteeState(str, enum.Enum):
    """
    Guarantee state for workflow.
    """

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BankGuarantee(Base):
    """
    Bank Guarantee model.
    """

    __tablename__ = "bank_guarantees"

    id = Column(Integer, primary_key=True, index=True)
    guarantee_number = Column(String(50), unique=True, nullable=False, index=True)

    # Guarantee Type
    guarantee_type = Column(Enum(GuaranteeType), nullable=False)

    # Status
    status = Column(Enum(GuaranteeStatus), default=GuaranteeStatus.DRAFT, index=True)
    state = Column(Enum(GuaranteeState), default=GuaranteeState.DRAFT, index=True)

    # Applicant (Requesting Party)
    applicant_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))
    applicant_name = Column(String(255))
    applicant_address = Column(Text)
    applicant_country = Column(String(100))

    # Beneficiary (Guarantee Holder)
    beneficiary_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="SET NULL")
    )
    beneficiary_name = Column(String(255))
    beneficiary_address = Column(Text)
    beneficiary_country = Column(String(100))

    # Issuing Bank
    issuing_bank_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="SET NULL")
    )
    issuing_bank_name = Column(String(255))
    issuing_bank_bic = Column(String(20))
    issuing_bank_address = Column(Text)

    # Amount & Currency
    currency = Column(String(3), nullable=False, default="USD")
    amount = Column(Numeric(18, 2), nullable=False)

    # Dates
    issue_date = Column(DateTime)
    effective_date = Column(DateTime)
    expiry_date = Column(DateTime)

    # Terms
    guarantee_terms = Column(Text)
    claim_conditions = Column(Text)

    # Undertaking Details
    undertaking_type = Column(String(50))  # Surety or Standby
    is_revokable = Column(Boolean, default=False)

    # Auto-renewal
    is_auto_renewal = Column(Boolean, default=False)
    renewal_period_days = Column(Integer)
    renewal_notice_days = Column(Integer)

    # Approval
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approved_at = Column(DateTime)
    approval_comments = Column(Text)

    # Rejection
    rejected_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    rejected_at = Column(DateTime)
    rejection_reason = Column(Text)

    # Claim
    claimed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    claimed_at = Column(DateTime)
    claim_amount = Column(Numeric(18, 2))
    claim_status = Column(String(50))

    # Release
    released_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    released_at = Column(DateTime)
    release_amount = Column(Numeric(18, 2))

    # User tracking
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    # Reference
    internal_reference = Column(String(50))
    external_reference = Column(String(50))
    related_lc_id = Column(
        Integer, ForeignKey("letters_of_credit.id", ondelete="SET NULL")
    )
    related_contract_id = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    applicant = relationship("Organization", foreign_keys=[applicant_id])
    beneficiary = relationship("Organization", foreign_keys=[beneficiary_id])
    issuing_bank = relationship("Organization", foreign_keys=[issuing_bank_id])
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<BankGuarantee(id={self.id}, guarantee_number='{self.guarantee_number}', amount={self.amount})>"
