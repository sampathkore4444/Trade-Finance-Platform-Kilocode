"""
Documentary Collection Model for Trade Finance Platform

This module defines the Documentary Collection database model.
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


class CollectionType(str, enum.Enum):
    """Documentary Collection types."""

    DA_DP = "da_dp"  # Documents Against Payment
    DA_DA = "da_da"  # Documents Against Acceptance


class CollectionStatus(str, enum.Enum):
    """Documentary Collection status."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    SENT_TO_BANK = "sent_to_bank"
    DOCUMENTS_RECEIVED = "documents_received"
    UNDER_EXAMINATION = "under_examination"
    PAYMENT_DONE = "payment_done"
    ACCEPTED = "accepted"
    DISHONORED = "dishonored"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class CollectionState(str, enum.Enum):
    """Collection state for workflow."""

    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DocumentaryCollection(Base):
    """Documentary Collection model."""

    __tablename__ = "documentary_collections"

    id = Column(Integer, primary_key=True, index=True)
    collection_number = Column(String(50), unique=True, nullable=False, index=True)

    # Collection Type
    collection_type = Column(Enum(CollectionType), nullable=False)

    # Status
    status = Column(Enum(CollectionStatus), default=CollectionStatus.DRAFT, index=True)
    state = Column(Enum(CollectionState), default=CollectionState.DRAFT, index=True)

    # Applicant (Drawer)
    applicant_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))
    applicant_name = Column(String(255))
    applicant_address = Column(Text)
    applicant_country = Column(String(100))

    # Beneficiary (Payee)
    beneficiary_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="SET NULL")
    )
    beneficiary_name = Column(String(255))
    beneficiary_address = Column(Text)
    beneficiary_country = Column(String(100))

    # Remitting Bank
    remitting_bank_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="SET NULL")
    )
    remitting_bank_name = Column(String(255))
    remitting_bank_bic = Column(String(20))

    # Collecting Bank
    collecting_bank_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="SET NULL")
    )
    collecting_bank_name = Column(String(255))
    collecting_bank_bic = Column(String(20))

    # Presenting Bank
    presenting_bank_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="SET NULL")
    )
    presenting_bank_name = Column(String(255))
    presenting_bank_bic = Column(String(20))

    # Amount & Currency
    currency = Column(String(3), nullable=False, default="USD")
    amount = Column(Numeric(18, 2), nullable=False)

    # Dates
    issue_date = Column(DateTime)
    due_date = Column(DateTime)
    accepted_due_date = Column(DateTime)

    # Documents
    documents_description = Column(Text)
    invoice_number = Column(String(100))

    # Acceptance details (for DA)
    accepted_at = Column(DateTime)
    acceptance_due_date = Column(DateTime)

    # Payment
    payment_date = Column(DateTime)
    payment_amount = Column(Numeric(18, 2))

    # Dishonor
    dishonored_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    dishonored_at = Column(DateTime)
    dishonor_reason = Column(Text)

    # Reference
    internal_reference = Column(String(50))
    related_lc_id = Column(
        Integer, ForeignKey("letters_of_credit.id", ondelete="SET NULL")
    )

    # User tracking
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return (
            f"<DocumentaryCollection(id={self.id}, number='{self.collection_number}')>"
        )
