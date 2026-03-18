"""
Documents Schemas
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum


class DocumentTypeEnum(str, Enum):
    CONTRACT = "contract"
    INVOICE = "invoice"
    BILL_OF_LADING = "bill_of_lading"
    CERTIFICATE = "certificate"
    OTHER = "other"


class DocumentBase(BaseModel):
    document_type: Optional[DocumentTypeEnum] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: int
    document_number: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    uploaded_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
