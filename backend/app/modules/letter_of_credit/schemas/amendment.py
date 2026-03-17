"""
LC Amendment Schemas for Trade Finance Platform

This module defines Pydantic schemas for LC Amendment operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class LCAmendmentBase(BaseModel):
    """Base LC Amendment schema."""

    increase_amount: Optional[Decimal] = None
    decrease_amount: Optional[Decimal] = None
    new_expiry_date: Optional[datetime] = None
    new_shipment_date: Optional[datetime] = None
    description: Optional[str] = None
    reason: Optional[str] = None


class LCAmendmentCreate(LCAmendmentBase):
    """LC Amendment creation schema."""

    pass


class LCAmendmentResponse(LCAmendmentBase):
    """LC Amendment response schema."""

    id: int
    lc_id: int
    amendment_number: int
    status: str
    amendment_date: Optional[datetime]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LCAmendmentListResponse(BaseModel):
    """LC Amendment list response schema."""

    items: List[LCAmendmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
