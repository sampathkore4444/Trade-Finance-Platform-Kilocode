"""
Documentary Collection Services Package
"""

from app.modules.documentary_collection.services.collection_service import (
    collection_service,
    DocumentaryCollectionService,
)

__all__ = [
    "collection_service",
    "DocumentaryCollectionService",
]
