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
    document_type: DocumentTypeEnum
    entity_type: str
    entity_id: int
    title: Optional[str] = None
    description: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: int
    document_number: str
    file_path: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    uploaded_by: Optional[int]

    model_config = ConfigDict(from_attributes=True)
