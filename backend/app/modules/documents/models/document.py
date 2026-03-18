"""
Documents Model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base
import enum


class DocumentType(str, enum.Enum):
    CONTRACT = "contract"
    INVOICE = "invoice"
    BILL_OF_LADING = "bill_of_lading"
    CERTIFICATE = "certificate"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_number = Column(String(50), unique=True)
    document_type = Column(Enum(DocumentType))
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    title = Column(String(255))
    description = Column(Text)
    file_path = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
