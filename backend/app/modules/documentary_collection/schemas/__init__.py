"""
Documentary Collection Schemas Package
"""

from app.modules.documentary_collection.schemas.collection import (
    DocumentaryCollectionBase,
    DocumentaryCollectionCreate,
    DocumentaryCollectionUpdate,
    DocumentaryCollectionResponse,
    CollectionListResponse,
)

__all__ = [
    "DocumentaryCollectionBase",
    "DocumentaryCollectionCreate",
    "DocumentaryCollectionUpdate",
    "DocumentaryCollectionResponse",
    "CollectionListResponse",
]
