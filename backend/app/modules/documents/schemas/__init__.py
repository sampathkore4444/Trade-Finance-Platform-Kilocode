"""
Documents Schemas Package
"""

from app.modules.documents.schemas.document import (
    DocumentBase,
    DocumentResponse,
    DocumentTypeEnum,
)

# Aliases for backward compatibility
DocumentUploadResponse = DocumentResponse
DocumentMetadataResponse = DocumentResponse
DocumentUpdate = DocumentBase
DocumentType = DocumentTypeEnum
DocumentStatus = DocumentTypeEnum

__all__ = [
    "DocumentBase",
    "DocumentResponse",
    "DocumentUploadResponse",
    "DocumentMetadataResponse",
    "DocumentUpdate",
    "DocumentTypeEnum",
    "DocumentType",
    "DocumentStatus",
]
