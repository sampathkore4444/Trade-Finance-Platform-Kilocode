"""
Document Service
"""

from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.documents.models import Document
from app.common.exceptions import NotFoundException
from app.common.helpers import generate_random_string


class DocumentService:
    async def generate_document_number(self) -> str:
        return f"DOC{generate_random_string(8, True)}"

    async def create_document(
        self,
        db: AsyncSession,
        document_type: str,
        entity_type: str,
        entity_id: int,
        uploaded_by: int,
        **kwargs,
    ) -> Document:
        doc = Document(
            document_number=await self.generate_document_number(),
            document_type=document_type,
            entity_type=entity_type,
            entity_id=entity_id,
            uploaded_by=uploaded_by,
            **kwargs,
        )
        db.add(doc)
        await db.flush()
        return doc


document_service = DocumentService()
