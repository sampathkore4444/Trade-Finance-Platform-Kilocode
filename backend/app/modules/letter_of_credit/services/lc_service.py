"""
Letter of Credit Service for Trade Finance Platform

This module contains business logic for Letter of Credit operations.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.letter_of_credit.models import (
    LetterOfCredit,
    LCAmendment,
    LCDocument,
    LCStatus,
    LCState,
    LCType,
    LCDocumentType,
)
from app.common.exceptions import (
    NotFoundException,
    ValidationException,
    BusinessRuleViolationException,
)
from app.common.helpers import generate_random_string
from app.core.security.audit_logger import audit_logger, AuditAction

# Import event generator
from app.modules.event_generator.services.event_factory import EventFactory
from app.modules.event_generator.services.event_repository import EventRepository
from app.modules.event_generator.services.event_generator import EventGenerator
from app.modules.event_generator.services.accounting_mapper import AccountingMapper


def _strip_tz(dt: Optional[datetime]) -> Optional[datetime]:
    """Strip timezone info from datetime to match database column type"""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


class LCService:
    """
    Service for Letter of Credit operations.
    """

    def __init__(self):
        self.event_factory = EventFactory()
        self.accounting_mapper = AccountingMapper()
    
    async def _generate_event(self, db: AsyncSession, event_type: str, lc: LetterOfCredit, 
                              user_id: int, accounting_entries: list = None):
        """Generate an event for LC action"""
        try:
            event_repo = EventRepository(db)
            event_generator = EventGenerator(
                db=db,
                event_factory=self.event_factory,
                event_repository=event_repo,
                event_publisher=None  # Events are published after commit
            )
            
            lc_data = {
                "id": str(lc.id),
                "reference": lc.lc_number,
                "applicant_party_id": str(lc.applicant_id) if lc.applicant_id else None,
                "beneficiary_party_id": str(lc.beneficiary_id) if lc.beneficiary_id else None,
                "type": lc.lc_type.value if lc.lc_type else None,
                "currency": lc.currency,
                "amount": str(lc.amount),
                "expiry_date": lc.expiry_date.isoformat() if lc.expiry_date else None,
                "issue_date": lc.issue_date.isoformat() if lc.issue_date else None,
                "issuing_bank": str(lc.issuing_bank_id) if lc.issuing_bank_id else None
            }
            
            event = event_generator.generate_lc_event(
                event_type=event_type,
                lc_data=lc_data,
                actor="user",
                actor_id=str(user_id),
                accounting_entries=accounting_entries,
                tenant_id=str(lc.organization_id) if hasattr(lc, 'organization_id') else None
            )
            
            return event
        except Exception as e:
            # Log but don't fail the main operation
            import logging
            logging.getLogger(__name__).error(f"Failed to generate event: {e}")
            return None

    async def generate_lc_number(self) -> str:
        """
        Generate a unique LC number.

        Returns:
            LC number string
        """
        prefix = "LC"
        date_part = datetime.utcnow().strftime("%Y%m%d")
        random_part = generate_random_string(6, include_digits=True)
        return f"{prefix}{date_part}{random_part}"

    async def create_lc(
        self,
        db: AsyncSession,
        lc_type: LCType,
        amount: Decimal,
        currency: str,
        created_by: int,
        **kwargs,
    ) -> LetterOfCredit:
        """
        Create a new Letter of Credit.

        Args:
            db: Database session
            lc_type: LC type
            amount: LC amount
            currency: Currency code
            created_by: User ID creating the LC
            **kwargs: Additional fields

        Returns:
            Created LC
        """
        # Generate LC number
        lc_number = await self.generate_lc_number()

        # Strip timezone from date fields to match database columns
        date_fields = ["issue_date", "expiry_date", "last_shipment_date"]
        for field in date_fields:
            if field in kwargs and kwargs[field]:
                kwargs[field] = _strip_tz(kwargs[field])

        # Create LC
        lc = LetterOfCredit(
            lc_number=lc_number,
            lc_type=lc_type,
            amount=amount,
            currency=currency,
            status=LCStatus.DRAFT,
            state=LCState.DRAFT,
            created_by=created_by,
            **kwargs,
        )

        db.add(lc)
        await db.flush()

        # Generate LC_CREATED event
        await self._generate_event(db, "LC_CREATED", lc, created_by)

        # Audit log
        audit_logger.log(
            action=AuditAction.LC_CREATED,
            user_id=created_by,
            resource_type="LC",
            resource_id=str(lc.id),
            details={
                "lc_number": lc_number,
                "amount": str(amount),
                "currency": currency,
            },
        )

        return lc

    async def get_lc_by_id(
        self,
        db: AsyncSession,
        lc_id: int,
    ) -> LetterOfCredit:
        """
        Get LC by ID.

        Args:
            db: Database session
            lc_id: LC ID

        Returns:
            LC

        Raises:
            NotFoundException: If LC not found
        """
        result = await db.execute(
            select(LetterOfCredit).where(LetterOfCredit.id == lc_id)
        )
        lc = result.scalar_one_or_none()

        if not lc:
            raise NotFoundException(
                message=f"Letter of Credit with ID {lc_id} not found"
            )

        return lc

    async def get_lc_by_number(
        self,
        db: AsyncSession,
        lc_number: str,
    ) -> Optional[LetterOfCredit]:
        """
        Get LC by LC number.

        Args:
            db: Database session
            lc_number: LC number

        Returns:
            LC or None
        """
        result = await db.execute(
            select(LetterOfCredit).where(LetterOfCredit.lc_number == lc_number)
        )
        return result.scalar_one_or_none()

    async def list_lcs(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status: Optional[LCStatus] = None,
        lc_type: Optional[LCType] = None,
        created_by: Optional[int] = None,
    ) -> Tuple[List[LetterOfCredit], int]:
        """
        List LCs with pagination.

        Args:
            db: Database session
            page: Page number
            page_size: Items per page
            search: Search query
            status: Filter by status
            lc_type: Filter by LC type
            created_by: Filter by creator

        Returns:
            Tuple of (LCs, total_count)
        """
        query = select(LetterOfCredit)

        # Apply filters
        filters = []
        if search:
            filters.append(
                or_(
                    LetterOfCredit.lc_number.ilike(f"%{search}%"),
                    LetterOfCredit.applicant_name.ilike(f"%{search}%"),
                    LetterOfCredit.beneficiary_name.ilike(f"%{search}%"),
                )
            )
        if status:
            filters.append(LetterOfCredit.status == status)
        if lc_type:
            filters.append(LetterOfCredit.lc_type == lc_type)
        if created_by:
            filters.append(LetterOfCredit.created_by == created_by)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(LetterOfCredit.created_at.desc())

        result = await db.execute(query)
        lcs = result.scalars().all()

        return list(lcs), total

    async def update_lc(
        self,
        db: AsyncSession,
        lc_id: int,
        user_id: int,
        **kwargs,
    ) -> LetterOfCredit:
        """
        Update LC.

        Args:
            db: Database session
            lc_id: LC ID
            user_id: User ID
            **kwargs: Fields to update

        Returns:
            Updated LC
        """
        lc = await self.get_lc_by_id(db, lc_id)

        # Only allow update in DRAFT state
        if lc.status != LCStatus.DRAFT:
            raise BusinessRuleViolationException(
                message="Only draft LCs can be updated"
            )

        # Update fields
        for key, value in kwargs.items():
            if hasattr(lc, key) and value is not None:
                setattr(lc, key, value)

        await db.flush()

        audit_logger.log(
            action=AuditAction.LC_UPDATED,
            user_id=user_id,
            resource_type="LC",
            resource_id=str(lc_id),
            details={"updated_fields": list(kwargs.keys())},
        )

        return lc

    async def submit_lc(
        self,
        db: AsyncSession,
        lc_id: int,
        user_id: int,
    ) -> LetterOfCredit:
        """
        Submit LC for approval.

        Args:
            db: Database session
            lc_id: LC ID
            user_id: User ID

        Returns:
            Updated LC
        """
        lc = await self.get_lc_by_id(db, lc_id)

        if lc.status != LCStatus.DRAFT:
            raise BusinessRuleViolationException(
                message="Only draft LCs can be submitted"
            )

        lc.status = LCStatus.SUBMITTED
        lc.state = LCState.PENDING_APPROVAL

        await db.flush()

        return lc

    async def approve_lc(
        self,
        db: AsyncSession,
        lc_id: int,
        user_id: int,
        comments: Optional[str] = None,
    ) -> LetterOfCredit:
        """
        Approve LC.

        Args:
            db: Database session
            lc_id: LC ID
            user_id: User ID approving
            comments: Approval comments

        Returns:
            Updated LC
        """
        lc = await self.get_lc_by_id(db, lc_id)

        if lc.status not in [LCStatus.SUBMITTED, LCStatus.UNDER_REVIEW]:
            raise BusinessRuleViolationException(
                message="LC cannot be approved in current state"
            )

        lc.status = LCStatus.APPROVED
        lc.state = LCState.ACTIVE
        lc.approved_by = user_id
        lc.approved_at = datetime.utcnow()
        lc.approval_comments = comments

        await db.flush()

        # Generate LC_APPROVED event
        await self._generate_event(db, "LC_APPROVED", lc, user_id)

        audit_logger.log(
            action=AuditAction.LC_APPROVED,
            user_id=user_id,
            resource_type="LC",
            resource_id=str(lc_id),
            details={"lc_number": lc.lc_number},
        )

        return lc

    async def reject_lc(
        self,
        db: AsyncSession,
        lc_id: int,
        user_id: int,
        reason: str,
    ) -> LetterOfCredit:
        """
        Reject LC.

        Args:
            db: Database session
            lc_id: LC ID
            user_id: User ID rejecting
            reason: Rejection reason

        Returns:
            Updated LC
        """
        lc = await self.get_lc_by_id(db, lc_id)

        if lc.status not in [LCStatus.SUBMITTED, LCStatus.UNDER_REVIEW]:
            raise BusinessRuleViolationException(
                message="LC cannot be rejected in current state"
            )

        lc.status = LCStatus.REJECTED
        lc.state = LCState.CANCELLED
        lc.rejected_by = user_id
        lc.rejected_at = datetime.utcnow()
        lc.rejection_reason = reason

        await db.flush()

        audit_logger.log(
            action=AuditAction.LC_REJECTED,
            user_id=user_id,
            resource_type="LC",
            resource_id=str(lc_id),
            details={"lc_number": lc.lc_number, "reason": reason},
        )

        return lc

    async def issue_lc(
        self,
        db: AsyncSession,
        lc_id: int,
        user_id: int,
    ) -> LetterOfCredit:
        """
        Issue LC (after approval).

        Args:
            db: Database session
            lc_id: LC ID
            user_id: User ID

        Returns:
            Updated LC
        """
        lc = await self.get_lc_by_id(db, lc_id)

        if lc.status != LCStatus.APPROVED:
            raise BusinessRuleViolationException(
                message="Only approved LCs can be issued"
            )

        lc.status = LCStatus.ISSUED
        lc.issue_date = datetime.utcnow()

        await db.flush()

        # Generate LC_ISSUED event with accounting entries
        # Create a mock event for the mapper
        class MockEvent:
            def __init__(self, event_type, payload):
                self.event_type = event_type
                self.payload = payload
        
        lc_data = {
            "id": str(lc.id),
            "reference": lc.lc_number,
            "applicant_party_id": str(lc.applicant_id) if lc.applicant_id else None,
            "beneficiary_party_id": str(lc.beneficiary_id) if lc.beneficiary_id else None,
            "type": lc.lc_type.value if lc.lc_type else None,
            "currency": lc.currency,
            "amount": str(lc.amount),
            "expiry_date": lc.expiry_date.isoformat() if lc.expiry_date else None,
            "issue_date": lc.issue_date.isoformat() if lc.issue_date else None,
            "issuing_bank": str(lc.issuing_bank_id) if lc.issuing_bank_id else None
        }
        mock_event = MockEvent("LC_ISSUED", lc_data)
        accounting_entries = self.accounting_mapper.map_to_entries(mock_event)
        
        await self._generate_event(db, "LC_ISSUED", lc, user_id, accounting_entries)

        return lc

    async def create_amendment(
        self,
        db: AsyncSession,
        lc_id: int,
        user_id: int,
        **kwargs,
    ) -> LCAmendment:
        """
        Create LC amendment.

        Args:
            db: Database session
            lc_id: LC ID
            user_id: User ID
            **kwargs: Amendment fields

        Returns:
            Created amendment
        """
        lc = await self.get_lc_by_id(db, lc_id)

        # Get last amendment number
        result = await db.execute(
            select(LCAmendment)
            .where(LCAmendment.lc_id == lc_id)
            .order_by(LCAmendment.amendment_number.desc())
            .limit(1)
        )
        last_amendment = result.scalar_one_or_none()

        amendment_number = (
            (last_amendment.amendment_number + 1) if last_amendment else 1
        )

        amendment = LCAmendment(
            lc_id=lc_id,
            amendment_number=amendment_number,
            **kwargs,
        )

        db.add(amendment)

        # Update LC status
        lc.status = LCStatus.AMENDED

        await db.flush()

        audit_logger.log(
            action=AuditAction.LC_AMENDED,
            user_id=user_id,
            resource_type="LC",
            resource_id=str(lc_id),
            details={"amendment_number": amendment_number},
        )

        return amendment

    async def add_document(
        self,
        db: AsyncSession,
        lc_id: int,
        document_type: LCDocumentType,
        document_name: Optional[str] = None,
        file_path: Optional[str] = None,
        **kwargs,
    ) -> LCDocument:
        """
        Add document to LC.

        Args:
            db: Database session
            lc_id: LC ID
            document_type: Type of document
            document_name: Document name
            file_path: File path
            **kwargs: Additional fields

        Returns:
            Created document
        """
        lc = await self.get_lc_by_id(db, lc_id)

        document = LCDocument(
            lc_id=lc_id,
            document_type=document_type,
            document_name=document_name,
            file_path=file_path,
            **kwargs,
        )

        db.add(document)
        await db.flush()

        return document

    async def review_document(
        self,
        db: AsyncSession,
        document_id: int,
        user_id: int,
        status: str,
        review_comments: Optional[str] = None,
    ) -> LCDocument:
        """
        Review LC document.

        Args:
            db: Database session
            document_id: Document ID
            user_id: User ID
            status: Review status
            review_comments: Review comments

        Returns:
            Updated document
        """
        result = await db.execute(
            select(LCDocument).where(LCDocument.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise NotFoundException(message=f"Document with ID {document_id} not found")

        document.status = status
        document.review_comments = review_comments
        document.reviewed_by = user_id
        document.reviewed_at = datetime.utcnow()

        await db.flush()

        return document

    async def delete_lc(
        self,
        db: AsyncSession,
        lc_id: int,
    ) -> None:
        """
        Delete LC.

        Args:
            db: Database session
            lc_id: LC ID
        """
        lc = await self.get_lc_by_id(db, lc_id)

        if lc.status != LCStatus.DRAFT:
            raise BusinessRuleViolationException(
                message="Only draft LCs can be deleted"
            )

        await db.delete(lc)
        await db.flush()


# Singleton instance
lc_service = LCService()
