"""
Letter of Credit Model for Trade Finance Platform

This module defines the Letter of Credit database model.
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


class LCType(str, enum.Enum):
    """
    Letter of Credit types.
    """

    IMPORT = "import"
    EXPORT = "export"
    STANDBY = "standby"
    TRANSFERABLE = "transferable"
    BACK_TO_BACK = "back_to_back"
    CONFIRMED = "confirmed"


class LCStatus(str, enum.Enum):
    """
    Letter of Credit status.
    """

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


class LCState(str, enum.Enum):
    """
    LC state for workflow.
    """

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LetterOfCredit(Base):
    """
    Letter of Credit model.
    """

    __tablename__ = "letters_of_credit"

    id = Column(Integer, primary_key=True, index=True)
    lc_number = Column(String(50), unique=True, nullable=False, index=True)

    # LC Type
    lc_type = Column(Enum(LCType), nullable=False, default=LCType.IMPORT)

    # Status
    status = Column(Enum(LCStatus), default=LCStatus.DRAFT, index=True)
    state = Column(Enum(LCState), default=LCState.DRAFT, index=True)

    # Applicant (Importer)
    applicant_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))
    applicant_name = Column(String(255))
    applicant_address = Column(Text)
    applicant_country = Column(String(100))

    # Beneficiary (Exporter)
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

    # Advising Bank
    advising_bank_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="SET NULL")
    )
    advising_bank_name = Column(String(255))
    advising_bank_bic = Column(String(20))

    # Confirming Bank (if any)
    confirming_bank_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="SET NULL")
    )
    confirming_bank_name = Column(String(255))
    confirming_bank_bic = Column(String(20))

    # Amount & Currency
    currency = Column(String(3), nullable=False, default="USD")
    amount = Column(Numeric(18, 2), nullable=False)
    tolerance_percent = Column(Numeric(5, 2), default=Decimal("10.00"))

    # Dates
    issue_date = Column(DateTime)
    expiry_date = Column(DateTime)
    expiry_place = Column(String(255))
    last_shipment_date = Column(DateTime)

    # Shipment Details
    shipment_from = Column(String(255))
    shipment_to = Column(String(255))
    partial_shipment = Column(Boolean, default=False)
    transhipment = Column(Boolean, default=False)
    shipping_terms = Column(String(100))

    # Description
    description_goods = Column(Text)
    description_services = Column(Text)

    # Additional Conditions
    additional_conditions = Column(Text)

    # Documents Required
    documents_required = Column(Text)

    # Charges
    charges_beneficiary = Column(Text)
    charges_applicant = Column(Text)

    # Reimbursement
    reimbursement_bank_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="SET NULL")
    )
    reimbursement_bank_name = Column(String(255))
    reimbursement_instructions = Column(Text)

    # SWIFT
    swift_mt700 = Column(Text)
    swift_mt701 = Column(Text)

    # Revocable
    is_revokable = Column(Boolean, default=False)
    is_confirmed = Column(Boolean, default=False)

    # Terms & Conditions
    ucp_version = Column(String(20), default="UCP 600")
    terms_conditions = Column(Text)

    # Approval
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approved_at = Column(DateTime)
    approval_comments = Column(Text)

    # Rejection
    rejected_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    rejected_at = Column(DateTime)
    rejection_reason = Column(Text)

    # User tracking
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    # Reference
    internal_reference = Column(String(50))
    external_reference = Column(String(50))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    applicant = relationship("Organization", foreign_keys=[applicant_id])
    beneficiary = relationship("Organization", foreign_keys=[beneficiary_id])
    issuing_bank = relationship("Organization", foreign_keys=[issuing_bank_id])
    creator = relationship("User", foreign_keys=[created_by])
    assignee = relationship("User", foreign_keys=[assigned_to])
    amendments = relationship(
        "LCAmendment", back_populates="lc", cascade="all, delete-orphan"
    )
    documents = relationship(
        "LCDocument", back_populates="lc", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<LetterOfCredit(id={self.id}, lc_number='{self.lc_number}', amount={self.amount})>"
