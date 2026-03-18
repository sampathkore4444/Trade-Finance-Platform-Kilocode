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

    # Applicant (Drawer)
    applicant_name: str = Field(..., min_length=1, max_length=255)
    applicant_address: Optional[str] = None
    applicant_country: Optional[str] = None

    # Beneficiary (Payee)
    beneficiary_name: str = Field(..., min_length=1, max_length=255)
    beneficiary_address: Optional[str] = None
    beneficiary_country: Optional[str] = None

    # Remitting Bank
    remitting_bank_name: Optional[str] = None
    remitting_bank_bic: Optional[str] = None

    # Collecting Bank
    collecting_bank_name: Optional[str] = None
    collecting_bank_bic: Optional[str] = None

    # Presenting Bank
    presenting_bank_name: Optional[str] = None
    presenting_bank_bic: Optional[str] = None

    # Amount
    currency: str = Field(..., min_length=3, max_length=3)
    amount: float = Field(..., gt=0)

    # Dates
    issue_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    # Documents
    documents_description: Optional[str] = None
    invoice_number: Optional[str] = None

    # Reference
    internal_reference: Optional[str] = None


class DocumentaryCollectionCreate(DocumentaryCollectionBase):
    """Schema for creating a new documentary collection"""

    pass


class DocumentaryCollectionUpdate(BaseModel):
    """Schema for updating a documentary collection"""

    collection_type: Optional[CollectionType] = None

    # Applicant (Drawer)
    applicant_name: Optional[str] = Field(None, min_length=1, max_length=255)
    applicant_address: Optional[str] = None
    applicant_country: Optional[str] = None

    # Beneficiary (Payee)
    beneficiary_name: Optional[str] = Field(None, min_length=1, max_length=255)
    beneficiary_address: Optional[str] = None
    beneficiary_country: Optional[str] = None

    # Remitting Bank
    remitting_bank_name: Optional[str] = None
    remitting_bank_bic: Optional[str] = None

    # Collecting Bank
    collecting_bank_name: Optional[str] = None
    collecting_bank_bic: Optional[str] = None

    # Presenting Bank
    presenting_bank_name: Optional[str] = None
    presenting_bank_bic: Optional[str] = None

    # Amount
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    amount: Optional[float] = Field(None, gt=0)

    # Dates
    issue_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    # Documents
    documents_description: Optional[str] = None
    invoice_number: Optional[str] = None

    # Reference
    internal_reference: Optional[str] = None

    # Remarks
    remarks: Optional[str] = None


class DocumentaryCollectionResponse(DocumentaryCollectionBase):
    """Schema for documentary collection response"""

    id: int
    collection_number: str
    status: CollectionStatus
    final_amount: Optional[float] = None
    remarks: Optional[str] = None
    status_history: List[dict] = []
    document_ids: List[str] = []
    created_by: int
    created_at: datetime
    updated_by: Optional[int] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CollectionListResponse(BaseModel):
    """Schema for paginated list response"""

    total: int
    skip: int
    limit: int
    items: List[DocumentaryCollectionResponse]
