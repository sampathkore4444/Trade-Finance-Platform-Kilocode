"""
LC Document Model for Trade Finance Platform

This module defines the LC Document database model.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
import enum


class LCDocumentType(str, enum.Enum):
    """
    Types of documents for LC.
    """

    BILL_OF_LADING = "bill_of_lading"
    COMMERCIAL_INVOICE = "commercial_invoice"
    PACKING_LIST = "packing_list"
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    INSURANCE_POLICY = "insurance_policy"
    INSPECTION_CERTIFICATE = "inspection_certificate"
    OTHER = "other"


class LCDocument(Base):
    """
    LC Document model.
    """

    __tablename__ = "lc_documents"

    id = Column(Integer, primary_key=True, index=True)
    lc_id = Column(
        Integer, ForeignKey("letters_of_credit.id", ondelete="CASCADE"), nullable=False
    )

    # Document Type
    document_type = Column(Enum(LCDocumentType), nullable=False)
    document_name = Column(String(255))
    description = Column(Text)

    # File
    file_path = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)
    mime_type = Column(String(100))

    # Status
    status = Column(
        String(50), default="pending"
    )  # pending, submitted, accepted, rejected
    review_comments = Column(Text)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    lc = relationship("LetterOfCredit", back_populates="documents")
    reviewer = relationship("User", foreign_keys=[reviewed_by])

    def __repr__(self):
        return (
            f"<LCDocument(id={self.id}, lc_id={self.lc_id}, type={self.document_type})>"
        )
