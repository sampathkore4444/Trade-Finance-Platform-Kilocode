"""
LC Amendment Model for Trade Finance Platform

This module defines the LC Amendment database model.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Numeric,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class LCAmendment(Base):
    """
    LC Amendment model.
    """

    __tablename__ = "lc_amendments"

    id = Column(Integer, primary_key=True, index=True)
    lc_id = Column(
        Integer, ForeignKey("letters_of_credit.id", ondelete="CASCADE"), nullable=False
    )
    amendment_number = Column(Integer, nullable=False)

    # Amendment Type
    increase_amount = Column(Numeric(18, 2))
    decrease_amount = Column(Numeric(18, 2))
    new_expiry_date = Column(DateTime)
    new_shipment_date = Column(DateTime)

    # Description
    description = Column(Text)
    reason = Column(Text)

    # Status
    status = Column(String(50), default="pending")  # pending, approved, rejected
    amendment_date = Column(DateTime)

    # Approval
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    approved_at = Column(DateTime)

    # SWIFT
    swift_mt707 = Column(Text)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    lc = relationship("LetterOfCredit", back_populates="amendments")

    def __repr__(self):
        return f"<LCAmendment(id={self.id}, lc_id={self.lc_id}, number={self.amendment_number})>"
