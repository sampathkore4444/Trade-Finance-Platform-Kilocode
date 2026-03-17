"""
Invoice Financing Schemas for Trade Finance Platform

This module defines Pydantic schemas for Invoice Financing operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class InvoiceStatusEnum(str, Enum):
    """Invoice status enumeration."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class FinancingStatusEnum(str, Enum):
    """Financing status enumeration."""

    NOT_FINANCED = "not_financed"
    FINANCING_REQUESTED = "financing_requested"
    UNDER_REVIEW = "under_review"
    FINANCED = "financed"
    REPAID = "repaid"
    DEFAULTED = "defaulted"


class InvoiceFinancingBase(BaseModel):
    """Base Invoice Financing schema."""

    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    seller_name: Optional[str] = None
    seller_address: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None

    currency: str = "USD"
    invoice_amount: Decimal = Field(..., gt=0)
    financed_amount: Optional[Decimal] = None
    outstanding_amount: Optional[Decimal] = None

    financing_rate: Optional[Decimal] = None
    financing_fee: Optional[Decimal] = None
    financing_start_date: Optional[datetime] = None
    financing_end_date: Optional[datetime] = None

    internal_reference: Optional[str] = None


class InvoiceFinancingCreate(InvoiceFinancingBase):
    """Invoice Financing creation schema."""

    seller_id: Optional[int] = None
    buyer_id: Optional[int] = None
    related_lc_id: Optional[int] = None


class InvoiceFinancingUpdate(BaseModel):
    """Invoice Financing update schema."""

    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    seller_name: Optional[str] = None
    seller_address: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None
    currency: Optional[str] = None
    invoice_amount: Optional[Decimal] = None
    internal_reference: Optional[str] = None


class InvoiceFinancingResponse(InvoiceFinancingBase):
    """Invoice Financing response schema."""

    id: int
    invoice_number: str
    invoice_status: InvoiceStatusEnum
    financing_status: FinancingStatusEnum

    seller_id: Optional[int]
    buyer_id: Optional[int]

    repaid_amount: Optional[Decimal]

    related_lc_id: Optional[int]
    created_by: Optional[int]

    payment_date: Optional[datetime]
    payment_amount: Optional[Decimal]

    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class InvoiceFinancingListResponse(BaseModel):
    """Invoice Financing list response schema."""

    items: List[InvoiceFinancingResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
