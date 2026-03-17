"""
Invoice Financing Model for Trade Finance Platform

This module defines the Invoice Financing database model.
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


class InvoiceStatus(str, enum.Enum):
    """Invoice status."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class FinancingStatus(str, enum.Enum):
    """Financing status."""

    NOT_FINANCED = "not_financed"
    FINANCING_REQUESTED = "financing_requested"
    UNDER_REVIEW = "under_review"
    FINANCED = "financed"
    REPAID = "repaid"
    DEFAULTED = "defaulted"


class InvoiceFinancing(Base):
    """Invoice Financing model."""

    __tablename__ = "invoice_financing"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)

    # Invoice Details
    invoice_date = Column(DateTime)
    due_date = Column(DateTime)

    # Status
    invoice_status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    financing_status = Column(
        Enum(FinancingStatus), default=FinancingStatus.NOT_FINANCED
    )

    # Seller ( borrower)
    seller_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))
    seller_name = Column(String(255))
    seller_address = Column(Text)

    # Buyer (debtor)
    buyer_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))
    buyer_name = Column(String(255))
    buyer_address = Column(Text)

    # Amounts
    currency = Column(String(3), nullable=False, default="USD")
    invoice_amount = Column(Numeric(18, 2), nullable=False)
    financed_amount = Column(Numeric(18, 2))
    outstanding_amount = Column(Numeric(18, 2))
    repaid_amount = Column(Numeric(18, 2))

    # Financing Details
    financing_rate = Column(Numeric(8, 4))
    financing_fee = Column(Numeric(18, 2))
    financing_start_date = Column(DateTime)
    financing_end_date = Column(DateTime)

    # Payment
    payment_date = Column(DateTime)
    payment_amount = Column(Numeric(18, 2))

    # Reference
    related_lc_id = Column(
        Integer, ForeignKey("letters_of_credit.id", ondelete="SET NULL")
    )
    internal_reference = Column(String(50))

    # User tracking
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<InvoiceFinancing(id={self.id}, invoice='{self.invoice_number}')>"
