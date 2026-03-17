"""
Documentary Collection Service
Handles business logic for documentary collections (import/export collections)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload

from app.modules.documentary_collection.models import DocumentaryCollection
from app.modules.documentary_collection.schemas import (
    DocumentaryCollectionCreate,
    DocumentaryCollectionUpdate,
    DocumentaryCollectionResponse,
)
from app.modules.documentary_collection.models import (
    DocumentaryCollection,
    CollectionStatus,
)


class DocumentaryCollectionService:
    """
    Service for managing documentary collections
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_collection(
        self,
        collection_data: DocumentaryCollectionCreate,
        user_id: UUID,
    ) -> DocumentaryCollection:
        """
        Create a new documentary collection
        """
        collection = DocumentaryCollection(
            collection_number=self._generate_collection_number(),
            collection_type=collection_data.collection_type,
            applicant_name=collection_data.applicant_name,
            applicant_account=collection_data.applicant_account,
            beneficiary_name=collection_data.beneficiary_name,
            beneficiary_bank=collection_data.beneficiary_bank,
            beneficiary_account=collection_data.beneficiary_account,
            currency=collection_data.currency,
            amount=collection_data.amount,
            tenor_days=collection_data.tenor_days,
            description=collection_data.description,
            # Shipment details
            port_of_loading=collection_data.port_of_loading,
            port_of_discharge=collection_data.port_of_discharge,
            goods_description=collection_data.goods_description,
            # Status
            status=CollectionStatus.DRAFT,
            created_by=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.db.add(collection)
        await self.db.commit()
        await self.db.refresh(collection)

        return collection

    async def get_collection_by_id(
        self, collection_id: UUID
    ) -> Optional[DocumentaryCollection]:
        """
        Get a documentary collection by ID
        """
        result = await self.db.execute(
            select(DocumentaryCollection)
            .where(DocumentaryCollection.id == collection_id)
            .options(selectinload(DocumentaryCollection.documents))
        )
        return result.scalar_one_or_none()

    async def get_collection_by_number(
        self, collection_number: str
    ) -> Optional[DocumentaryCollection]:
        """
        Get a documentary collection by collection number
        """
        result = await self.db.execute(
            select(DocumentaryCollection)
            .where(DocumentaryCollection.collection_number == collection_number)
            .options(selectinload(DocumentaryCollection.documents))
        )
        return result.scalar_one_or_none()

    async def list_collections(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[CollectionStatus] = None,
        applicant_name: Optional[str] = None,
        beneficiary_name: Optional[str] = None,
    ) -> List[DocumentaryCollection]:
        """
        List documentary collections with optional filters
        """
        query = select(DocumentaryCollection)

        if status:
            query = query.where(DocumentaryCollection.status == status)

        if applicant_name:
            query = query.where(
                DocumentaryCollection.applicant_name.ilike(f"%{applicant_name}%")
            )

        if beneficiary_name:
            query = query.where(
                DocumentaryCollection.beneficiary_name.ilike(f"%{beneficiary_name}%")
            )

        query = (
            query.offset(skip)
            .limit(limit)
            .order_by(DocumentaryCollection.created_at.desc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_collection(
        self,
        collection_id: UUID,
        collection_data: DocumentaryCollectionUpdate,
        user_id: UUID,
    ) -> Optional[DocumentaryCollection]:
        """
        Update a documentary collection
        """
        collection = await self.get_collection_by_id(collection_id)
        if not collection:
            return None

        update_data = collection_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        update_data["updated_by"] = user_id

        for key, value in update_data.items():
            setattr(collection, key, value)

        await self.db.commit()
        await self.db.refresh(collection)

        return collection

    async def update_status(
        self,
        collection_id: UUID,
        new_status: CollectionStatus,
        user_id: UUID,
        remarks: Optional[str] = None,
    ) -> Optional[DocumentaryCollection]:
        """
        Update the status of a documentary collection
        """
        collection = await self.get_collection_by_id(collection_id)
        if not collection:
            return None

        old_status = collection.status
        collection.status = new_status
        collection.updated_at = datetime.utcnow()
        collection.updated_by = user_id

        if remarks:
            collection.remarks = remarks

        # Add status history
        if not collection.status_history:
            collection.status_history = []

        collection.status_history.append(
            {
                "from_status": old_status.value,
                "to_status": new_status.value,
                "changed_by": str(user_id),
                "changed_at": datetime.utcnow().isoformat(),
                "remarks": remarks or "",
            }
        )

        await self.db.commit()
        await self.db.refresh(collection)

        return collection

    async def submit_for_approval(
        self, collection_id: UUID, user_id: UUID
    ) -> Optional[DocumentaryCollection]:
        """
        Submit documentary collection for approval
        """
        return await self.update_status(
            collection_id=collection_id,
            new_status=CollectionStatus.PENDING_APPROVAL,
            user_id=user_id,
            remarks="Submitted for approval",
        )

    async def approve_collection(
        self,
        collection_id: UUID,
        user_id: UUID,
        remarks: Optional[str] = None,
    ) -> Optional[DocumentaryCollection]:
        """
        Approve a documentary collection
        """
        return await self.update_status(
            collection_id=collection_id,
            new_status=CollectionStatus.APPROVED,
            user_id=user_id,
            remarks=remarks or "Approved",
        )

    async def reject_collection(
        self,
        collection_id: UUID,
        user_id: UUID,
        reason: str,
    ) -> Optional[DocumentaryCollection]:
        """
        Reject a documentary collection
        """
        return await self.update_status(
            collection_id=collection_id,
            new_status=CollectionStatus.REJECTED,
            user_id=user_id,
            remarks=reason,
        )

    async def process_collection(
        self, collection_id: UUID, user_id: UUID
    ) -> Optional[DocumentaryCollection]:
        """
        Process the documentary collection (after approval)
        """
        return await self.update_status(
            collection_id=collection_id,
            new_status=CollectionStatus.PROCESSING,
            user_id=user_id,
            remarks="Collection is being processed",
        )

    async def complete_collection(
        self,
        collection_id: UUID,
        user_id: UUID,
        final_amount: Optional[float] = None,
    ) -> Optional[DocumentaryCollection]:
        """
        Mark documentary collection as completed
        """
        collection = await self.get_collection_by_id(collection_id)
        if not collection:
            return None

        if final_amount:
            collection.final_amount = final_amount

        return await self.update_status(
            collection_id=collection_id,
            new_status=CollectionStatus.COMPLETED,
            user_id=user_id,
            remarks="Collection completed",
        )

    async def cancel_collection(
        self,
        collection_id: UUID,
        user_id: UUID,
        reason: str,
    ) -> Optional[DocumentaryCollection]:
        """
        Cancel a documentary collection
        """
        return await self.update_status(
            collection_id=collection_id,
            new_status=CollectionStatus.CANCELLED,
            user_id=user_id,
            remarks=f"Cancelled: {reason}",
        )

    async def add_document(
        self,
        collection_id: UUID,
        document_id: UUID,
    ) -> Optional[DocumentaryCollection]:
        """
        Add a document to the collection
        """
        collection = await self.get_collection_by_id(collection_id)
        if not collection:
            return None

        if not collection.document_ids:
            collection.document_ids = []

        collection.document_ids.append(str(document_id))
        collection.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(collection)

        return collection

    def _generate_collection_number(self) -> str:
        """
        Generate a unique collection number
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"DC{timestamp}"

    async def get_collections_by_applicant(
        self,
        applicant_account: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DocumentaryCollection]:
        """
        Get collections by applicant account
        """
        result = await self.db.execute(
            select(DocumentaryCollection)
            .where(DocumentaryCollection.applicant_account == applicant_account)
            .offset(skip)
            .limit(limit)
            .order_by(DocumentaryCollection.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_collections_by_beneficiary(
        self,
        beneficiary_account: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DocumentaryCollection]:
        """
        Get collections by beneficiary account
        """
        result = await self.db.execute(
            select(DocumentaryCollection)
            .where(DocumentaryCollection.beneficiary_account == beneficiary_account)
            .offset(skip)
            .limit(limit)
            .order_by(DocumentaryCollection.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_pending_collections(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DocumentaryCollection]:
        """
        Get all pending collections
        """
        result = await self.db.execute(
            select(DocumentaryCollection)
            .where(DocumentaryCollection.status == CollectionStatus.PENDING_APPROVAL)
            .offset(skip)
            .limit(limit)
            .order_by(DocumentaryCollection.created_at.asc())
        )
        return list(result.scalars().all())


# Service instance factory
collection_service = DocumentaryCollectionService
