"""
Documentary Collection Schemas
Pydantic models for documentary collection API
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

# Import enums from models
from app.modules.documentary_collection.models import CollectionType, CollectionStatus


class DocumentaryCollectionBase(BaseModel):
    """Base schema for documentary collection"""
    collection_type: CollectionType
    applicant_name: str = Field(..., min_length=1, max_length=255)
    applicant_account: str = Field(..., min_length=1, max_length=50)
    beneficiary_name: str = Field(..., min_length=1, max_length=255)
    beneficiary_bank: str = Field(..., min_length=1, max_length=255)
    beneficiary_account: str = Field(..., min_length=1, max_length=50)
    currency: str = Field(..., min_length=3, max_length=3)
    amount: float = Field(..., gt=0)
    tenor_days: int = Field(..., ge=0)
    description: Optional[str] = None
    port_of_loading: Optional[str] = None
    port_of_discharge: Optional[str] = None
    goods_description: Optional[str] = None


class DocumentaryCollectionCreate(DocumentaryCollectionBase):
    """Schema for creating a new documentary collection"""
    pass


class DocumentaryCollectionUpdate(BaseModel):
    """Schema for updating a documentary collection"""
    collection_type: Optional[CollectionType] = None
    applicant_name: Optional[str] = Field(None, min_length=1, max_length=255)
    applicant_account: Optional[str] = Field(None, min_length=1, max_length=50)
    beneficiary_name: Optional[str] = Field(None, min_length=1, max_length=255)
    beneficiary_bank: Optional[str] = Field(None, min_length=1, max_length=255)
    beneficiary_account: Optional[str] = Field(None, min_length=1, max_length=50)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    amount: Optional[float] = Field(None, gt=0)
    tenor_days: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
    port_of_loading: Optional[str] = None
    port_of_discharge: Optional[str] = None
    goods_description: Optional[str] = None
    remarks: Optional[str] = None


class DocumentaryCollectionResponse(DocumentaryCollectionBase):
    """Schema for documentary collection response"""
    id: UUID
    collection_number: str
    status: CollectionStatus
    final_amount: Optional[float] = None
    remarks: Optional[str] = None
    status_history: List[dict] = []
    document_ids: List[str] = []
    created_by: UUID
    created_at: datetime
    updated_by: Optional[UUID] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CollectionListResponse(BaseModel):
    """Schema for paginated list response"""
    total: int
    skip: int
    limit: int
    items: List[DocumentaryCollectionResponse]
