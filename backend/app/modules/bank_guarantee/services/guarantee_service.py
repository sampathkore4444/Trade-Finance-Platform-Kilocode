"""
Bank Guarantee Service for Trade Finance Platform

This module contains business logic for Bank Guarantee operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bank_guarantee.models import (
    BankGuarantee,
    GuaranteeType,
    GuaranteeStatus,
    GuaranteeState,
)
from app.common.exceptions import (
    NotFoundException,
    ValidationException,
    BusinessRuleViolationException,
)
from app.common.helpers import generate_random_string
from app.core.security.audit_logger import audit_logger, AuditAction


class GuaranteeService:
    """
    Service for Bank Guarantee operations.
    """

    async def generate_guarantee_number(self) -> str:
        """
        Generate a unique Guarantee number.

        Returns:
            Guarantee number string
        """
        prefix = "BG"
        date_part = datetime.utcnow().strftime("%Y%m%d")
        random_part = generate_random_string(6, include_digits=True)
        return f"{prefix}{date_part}{random_part}"

    async def create_guarantee(
        self,
        db: AsyncSession,
        guarantee_type: GuaranteeType,
        amount: Decimal,
        currency: str,
        created_by: int,
        **kwargs,
    ) -> BankGuarantee:
        """
        Create a new Bank Guarantee.

        Args:
            db: Database session
            guarantee_type: Guarantee type
            amount: Guarantee amount
            currency: Currency code
            created_by: User ID creating the guarantee
            **kwargs: Additional fields

        Returns:
            Created guarantee
        """
        # Generate guarantee number
        guarantee_number = await self.generate_guarantee_number()

        # Create guarantee
        guarantee = BankGuarantee(
            guarantee_number=guarantee_number,
            guarantee_type=guarantee_type,
            amount=amount,
            currency=currency,
            status=GuaranteeStatus.DRAFT,
            state=GuaranteeState.DRAFT,
            created_by=created_by,
            **kwargs,
        )

        db.add(guarantee)
        await db.flush()

        audit_logger.log(
            action=AuditAction.GUARANTEE_CREATED,
            user_id=created_by,
            resource_type="GUARANTEE",
            resource_id=str(guarantee.id),
            details={
                "guarantee_number": guarantee_number,
                "amount": str(amount),
                "currency": currency,
            },
        )

        return guarantee

    async def get_guarantee_by_id(
        self,
        db: AsyncSession,
        guarantee_id: int,
    ) -> BankGuarantee:
        """
        Get guarantee by ID.

        Args:
            db: Database session
            guarantee_id: Guarantee ID

        Returns:
            Guarantee

        Raises:
            NotFoundException: If guarantee not found
        """
        result = await db.execute(
            select(BankGuarantee).where(BankGuarantee.id == guarantee_id)
        )
        guarantee = result.scalar_one_or_none()

        if not guarantee:
            raise NotFoundException(
                message=f"Bank Guarantee with ID {guarantee_id} not found"
            )

        return guarantee

    async def get_guarantee_by_number(
        self,
        db: AsyncSession,
        guarantee_number: str,
    ) -> Optional[BankGuarantee]:
        """
        Get guarantee by guarantee number.

        Args:
            db: Database session
            guarantee_number: Guarantee number

        Returns:
            Guarantee or None
        """
        result = await db.execute(
            select(BankGuarantee).where(
                BankGuarantee.guarantee_number == guarantee_number
            )
        )
        return result.scalar_one_or_none()

    async def list_guarantees(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status: Optional[GuaranteeStatus] = None,
        guarantee_type: Optional[GuaranteeType] = None,
        created_by: Optional[int] = None,
    ) -> Tuple[List[BankGuarantee], int]:
        """
        List guarantees with pagination.

        Args:
            db: Database session
            page: Page number
            page_size: Items per page
            search: Search query
            status: Filter by status
            guarantee_type: Filter by guarantee type
            created_by: Filter by creator

        Returns:
            Tuple of (guarantees, total_count)
        """
        query = select(BankGuarantee)

        # Apply filters
        filters = []
        if search:
            filters.append(
                or_(
                    BankGuarantee.guarantee_number.ilike(f"%{search}%"),
                    BankGuarantee.applicant_name.ilike(f"%{search}%"),
                    BankGuarantee.beneficiary_name.ilike(f"%{search}%"),
                )
            )
        if status:
            filters.append(BankGuarantee.status == status)
        if guarantee_type:
            filters.append(BankGuarantee.guarantee_type == guarantee_type)
        if created_by:
            filters.append(BankGuarantee.created_by == created_by)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(BankGuarantee.created_at.desc())

        result = await db.execute(query)
        guarantees = result.scalars().all()

        return list(guarantees), total

    async def update_guarantee(
        self,
        db: AsyncSession,
        guarantee_id: int,
        user_id: int,
        **kwargs,
    ) -> BankGuarantee:
        """
        Update guarantee.

        Args:
            db: Database session
            guarantee_id: Guarantee ID
            user_id: User ID
            **kwargs: Fields to update

        Returns:
            Updated guarantee
        """
        guarantee = await self.get_guarantee_by_id(db, guarantee_id)

        # Only allow update in DRAFT state
        if guarantee.status != GuaranteeStatus.DRAFT:
            raise BusinessRuleViolationException(
                message="Only draft guarantees can be updated"
            )

        # Update fields
        for key, value in kwargs.items():
            if hasattr(guarantee, key) and value is not None:
                setattr(guarantee, key, value)

        await db.flush()

        audit_logger.log(
            action=AuditAction.GUARANTEE_UPDATED,
            user_id=user_id,
            resource_type="GUARANTEE",
            resource_id=str(guarantee_id),
            details={"updated_fields": list(kwargs.keys())},
        )

        return guarantee

    async def submit_guarantee(
        self,
        db: AsyncSession,
        guarantee_id: int,
        user_id: int,
    ) -> BankGuarantee:
        """
        Submit guarantee for approval.

        Args:
            db: Database session
            guarantee_id: Guarantee ID
            user_id: User ID

        Returns:
            Updated guarantee
        """
        guarantee = await self.get_guarantee_by_id(db, guarantee_id)

        if guarantee.status != GuaranteeStatus.DRAFT:
            raise BusinessRuleViolationException(
                message="Only draft guarantees can be submitted"
            )

        guarantee.status = GuaranteeStatus.SUBMITTED
        guarantee.state = GuaranteeState.PENDING_APPROVAL

        await db.flush()

        return guarantee

    async def approve_guarantee(
        self,
        db: AsyncSession,
        guarantee_id: int,
        user_id: int,
        comments: Optional[str] = None,
    ) -> BankGuarantee:
        """
        Approve guarantee.

        Args:
            db: Database session
            guarantee_id: Guarantee ID
            user_id: User ID approving
            comments: Approval comments

        Returns:
            Updated guarantee
        """
        guarantee = await self.get_guarantee_by_id(db, guarantee_id)

        if guarantee.status not in [
            GuaranteeStatus.SUBMITTED,
            GuaranteeStatus.UNDER_REVIEW,
        ]:
            raise BusinessRuleViolationException(
                message="Guarantee cannot be approved in current state"
            )

        guarantee.status = GuaranteeStatus.APPROVED
        guarantee.state = GuaranteeState.ACTIVE
        guarantee.approved_by = user_id
        guarantee.approved_at = datetime.utcnow()
        guarantee.approval_comments = comments

        await db.flush()

        audit_logger.log(
            action=AuditAction.GUARANTEE_APPROVED,
            user_id=user_id,
            resource_type="GUARANTEE",
            resource_id=str(guarantee_id),
            details={"guarantee_number": guarantee.guarantee_number},
        )

        return guarantee

    async def reject_guarantee(
        self,
        db: AsyncSession,
        guarantee_id: int,
        user_id: int,
        reason: str,
    ) -> BankGuarantee:
        """
        Reject guarantee.

        Args:
            db: Database session
            guarantee_id: Guarantee ID
            user_id: User ID rejecting
            reason: Rejection reason

        Returns:
            Updated guarantee
        """
        guarantee = await self.get_guarantee_by_id(db, guarantee_id)

        if guarantee.status not in [
            GuaranteeStatus.SUBMITTED,
            GuaranteeStatus.UNDER_REVIEW,
        ]:
            raise BusinessRuleViolationException(
                message="Guarantee cannot be rejected in current state"
            )

        guarantee.status = GuaranteeStatus.REJECTED
        guarantee.state = GuaranteeState.CANCELLED
        guarantee.rejected_by = user_id
        guarantee.rejected_at = datetime.utcnow()
        guarantee.rejection_reason = reason

        await db.flush()

        audit_logger.log(
            action=AuditAction.GUARANTEE_REJECTED,
            user_id=user_id,
            resource_type="GUARANTEE",
            resource_id=str(guarantee_id),
            details={"guarantee_number": guarantee.guarantee_number, "reason": reason},
        )

        return guarantee

    async def issue_guarantee(
        self,
        db: AsyncSession,
        guarantee_id: int,
        user_id: int,
    ) -> BankGuarantee:
        """
        Issue guarantee (after approval).

        Args:
            db: Database session
            guarantee_id: Guarantee ID
            user_id: User ID

        Returns:
            Updated guarantee
        """
        guarantee = await self.get_guarantee_by_id(db, guarantee_id)

        if guarantee.status != GuaranteeStatus.APPROVED:
            raise BusinessRuleViolationException(
                message="Only approved guarantees can be issued"
            )

        guarantee.status = GuaranteeStatus.ISSUED
        guarantee.issue_date = datetime.utcnow()

        await db.flush()

        return guarantee

    async def claim_guarantee(
        self,
        db: AsyncSession,
        guarantee_id: int,
        user_id: int,
        claim_amount: Decimal,
        claim_reason: str,
    ) -> BankGuarantee:
        """
        Claim against guarantee.

        Args:
            db: Database session
            guarantee_id: Guarantee ID
            user_id: User ID claiming
            claim_amount: Claim amount
            claim_reason: Claim reason

        Returns:
            Updated guarantee
        """
        guarantee = await self.get_guarantee_by_id(db, guarantee_id)

        if guarantee.status not in [
            GuaranteeStatus.ISSUED,
            GuaranteeStatus.ACTIVE,
        ]:
            raise BusinessRuleViolationException(
                message="Cannot claim against guarantee in current state"
            )

        guarantee.claimed_by = user_id
        guarantee.claimed_at = datetime.utcnow()
        guarantee.claim_amount = claim_amount
        guarantee.claim_status = "pending"
        guarantee.status = GuaranteeStatus.CLAIMED

        await db.flush()

        audit_logger.log(
            action=AuditAction.GUARANTEE_CLAIMED,
            user_id=user_id,
            resource_type="GUARANTEE",
            resource_id=str(guarantee_id),
            details={
                "guarantee_number": guarantee.guarantee_number,
                "claim_amount": str(claim_amount),
            },
        )

        return guarantee

    async def release_guarantee(
        self,
        db: AsyncSession,
        guarantee_id: int,
        user_id: int,
        release_amount: Optional[Decimal] = None,
        release_reason: Optional[str] = None,
    ) -> BankGuarantee:
        """
        Release guarantee.

        Args:
            db: Database session
            guarantee_id: Guarantee ID
            user_id: User ID releasing
            release_amount: Release amount
            release_reason: Release reason

        Returns:
            Updated guarantee
        """
        guarantee = await self.get_guarantee_by_id(db, guarantee_id)

        if guarantee.status not in [
            GuaranteeStatus.ISSUED,
            GuaranteeStatus.ACTIVE,
            GuaranteeStatus.CLAIMED,
        ]:
            raise BusinessRuleViolationException(
                message="Cannot release guarantee in current state"
            )

        guarantee.released_by = user_id
        guarantee.released_at = datetime.utcnow()
        guarantee.release_amount = release_amount or guarantee.amount
        guarantee.status = GuaranteeStatus.RELEASED

        await db.flush()

        audit_logger.log(
            action=AuditAction.GUARANTEE_RELEASED,
            user_id=user_id,
            resource_type="GUARANTEE",
            resource_id=str(guarantee_id),
            details={"guarantee_number": guarantee.guarantee_number},
        )

        return guarantee

    async def cancel_guarantee(
        self,
        db: AsyncSession,
        guarantee_id: int,
        user_id: int,
        reason: str,
    ) -> BankGuarantee:
        """
        Cancel guarantee.

        Args:
            db: Database session
            guarantee_id: Guarantee ID
            user_id: User ID cancelling
            reason: Cancellation reason

        Returns:
            Updated guarantee
        """
        guarantee = await self.get_guarantee_by_id(db, guarantee_id)

        if guarantee.status not in [
            GuaranteeStatus.DRAFT,
            GuaranteeStatus.SUBMITTED,
        ]:
            raise BusinessRuleViolationException(
                message="Cannot cancel guarantee in current state"
            )

        guarantee.cancelled_by = user_id
        guarantee.cancelled_at = datetime.utcnow()
        guarantee.cancellation_reason = reason
        guarantee.status = GuaranteeStatus.CANCELLED

        await db.flush()

        audit_logger.log(
            action=AuditAction.GUARANTEE_CANCELLED,
            user_id=user_id,
            resource_type="GUARANTEE",
            resource_id=str(guarantee_id),
            details={"guarantee_number": guarantee.guarantee_number, "reason": reason},
        )

        return guarantee


# Singleton instance
guarantee_service = GuaranteeService()
