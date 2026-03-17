"""
LC Document Schemas for Trade Finance Platform

This module defines Pydantic schemas for LC Document operations.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from enum import Enum


class LCDocumentTypeEnum(str, Enum):
    """LC Document type enumeration."""

    BILL_OF_LADING = "bill_of_lading"
    COMMERCIAL_INVOICE = "commercial_invoice"
    PACKING_LIST = "packing_list"
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    INSURANCE_POLICY = "insurance_policy"
    INSPECTION_CERTIFICATE = "inspection_certificate"
    OTHER = "other"


class LCDocumentBase(BaseModel):
    """Base LC Document schema."""

    document_type: LCDocumentTypeEnum
    document_name: Optional[str] = None
    description: Optional[str] = None


class LCDocumentCreate(LCDocumentBase):
    """LC Document creation schema."""

    pass


class LCDocumentResponse(LCDocumentBase):
    """LC Document response schema."""

    id: int
    lc_id: int
    file_path: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    status: str
    review_comments: Optional[str]
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LCDocumentReview(BaseModel):
    """LC Document review schema."""

    status: str
    review_comments: Optional[str] = None


class LCDocumentListResponse(BaseModel):
    """LC Document list response schema."""

    items: List[LCDocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
