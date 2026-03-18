"""
Document Service
"""

import os
import uuid
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.models import Document
from app.common.helpers import generate_random_string

# Base upload directory
UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class DocumentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_document_number(self) -> str:
        return f"DOC{generate_random_string(8, True)}"

    async def upload_document(
        self,
        file,
        document_type: Optional[str],
        entity_type: Optional[str],
        entity_id: Optional[int],
        user_id: int,
    ) -> Document:
        """Upload and save a document"""
        # Save file to disk
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        file_path = UPLOAD_DIR / f"{file_id}{file_extension}"

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Create document record
        doc = Document(
            document_number=await self.generate_document_number(),
            file_name=file.filename or "unknown",
            file_path=str(file_path),
            file_size=len(content),
            mime_type=file.content_type or "application/octet-stream",
            document_type=document_type,
            entity_type=entity_type,
            entity_id=entity_id,
            uploaded_by=user_id,
        )
        self.db.add(doc)
        await self.db.flush()
        await self.db.refresh(doc)
        return doc

    async def list_documents(
        self,
        skip: int = 0,
        limit: int = 100,
        document_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Document]:
        """List documents with filters"""
        query = select(Document)

        filters = []
        if document_type:
            filters.append(Document.document_type == document_type)
        if entity_type:
            filters.append(Document.entity_type == entity_type)
        if entity_id:
            filters.append(Document.entity_id == entity_id)

        if filters:
            query = query.where(and_(*filters))

        query = query.offset(skip).limit(limit).order_by(Document.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        query = select(Document).where(Document.id == document_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_document_path(self, document_id: int) -> Optional[str]:
        """Get the file path for a document"""
        doc = await self.get_document_by_id(document_id)
        if doc and doc.file_path:
            return doc.file_path
        return None

    async def update_document(
        self,
        document_id: int,
        document_data: dict,
        user_id: int,
    ) -> Optional[Document]:
        """Update document metadata"""
        doc = await self.get_document_by_id(document_id)
        if not doc:
            return None

        for key, value in document_data.items():
            if hasattr(doc, key) and value is not None:
                setattr(doc, key, value)

        await self.db.flush()
        await self.db.refresh(doc)
        return doc

    async def delete_document(self, document_id: int, user_id: int) -> bool:
        """Delete a document"""
        doc = await self.get_document_by_id(document_id)
        if not doc:
            return False

        # Delete file from disk
        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)

        await self.db.delete(doc)
        await self.db.flush()
        return True

    async def verify_document(
        self, document_id: int, user_id: int
    ) -> Optional[Document]:
        """Verify document is not implemented in base model - just return the document"""
        doc = await self.get_document_by_id(document_id)
        return doc

    async def reject_document(
        self, document_id: int, reason: str, user_id: int
    ) -> Optional[Document]:
        """Reject document is not implemented in base model - just return the document"""
        doc = await self.get_document_by_id(document_id)
        return doc

    async def get_documents_by_entity(
        self,
        entity_type: str,
        entity_id: int,
    ) -> List[Document]:
        """Get all documents for a specific entity"""
        query = (
            select(Document)
            .where(
                and_(
                    Document.entity_type == entity_type, Document.entity_id == entity_id
                )
            )
            .order_by(Document.created_at.desc())
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_pending_documents(
        self, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """Get all pending documents - returns all documents in base model"""
        query = (
            select(Document)
            .offset(skip)
            .limit(limit)
            .order_by(Document.created_at.desc())
        )

        result = await self.db.execute(query)
        return result.scalars().all()
