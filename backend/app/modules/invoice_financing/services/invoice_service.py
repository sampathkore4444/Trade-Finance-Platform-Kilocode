"""
Invoice Financing Service for Trade Finance Platform

This module contains business logic for Invoice Financing operations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession


from app.modules.invoice_financing.models import (
    InvoiceFinancing,
    InvoiceStatus,
    FinancingStatus,
)
from app.common.exceptions import (
    NotFoundException,
    BusinessRuleViolationException,
)
from app.common.helpers import generate_random_string
from app.core.security.audit_logger import audit_logger, AuditAction

# Import event generator
from app.modules.event_generator.services.event_factory import EventFactory
from app.modules.event_generator.services.event_repository import EventRepository
from app.modules.event_generator.services.event_generator import EventGenerator


def _strip_tz(dt: Optional[datetime]) -> Optional[datetime]:
    """Strip timezone info from datetime to match database column type."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


class InvoiceFinancingService:
    """Service for Invoice Financing operations."""

    def __init__(self):
        self.event_factory = EventFactory()
    
    async def _generate_event(self, db: AsyncSession, event_type: str, invoice: InvoiceFinancing, 
                              user_id: int):
        """Generate an event for Invoice action"""
        try:
            event_repo = EventRepository(db)
            event_generator = EventGenerator(
                db=db,
                event_factory=self.event_factory,
                event_repository=event_repo,
                event_publisher=None
            )
            
            invoice_data = {
                "id": str(invoice.id),
                "reference": invoice.invoice_number,
                "sellerPartyId": str(invoice.seller_id) if invoice.seller_id else None,
                "buyerPartyId": str(invoice.buyer_id) if invoice.buyer_id else None,
                "currency": invoice.currency,
                "amount": str(invoice.invoice_amount),
                "invoiceDate": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                "dueDate": invoice.due_date.isoformat() if invoice.due_date else None
            }
            
            event = event_generator.generate_event(
                event_type=event_type,
                payload=invoice_data,
                source_service="invoice_service",
                source_actor="user",
                source_actor_id=str(user_id),
                tenant_id=str(invoice.organization_id) if hasattr(invoice, 'organization_id') else None
            )
            
            return event
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to generate event: {e}")
            return None

    async def generate_invoice_number(self) -> str:
        """Generate a unique invoice number."""
        prefix = "INV"
        date_part = datetime.utcnow().strftime("%Y%m%d")
        random_part = generate_random_string(6, include_digits=True)
        return f"{prefix}{date_part}{random_part}"

    async def create_invoice(
        self,
        db: AsyncSession,
        invoice_amount: Decimal,
        currency: str,
        created_by: int,
        **kwargs,
    ) -> InvoiceFinancing:
        """Create a new Invoice Financing."""
        # Strip timezone from date fields to match database columns
        date_fields = [
            "invoice_date",
            "due_date",
            "financing_start_date",
            "financing_end_date",
        ]
        for field in date_fields:
            if field in kwargs and kwargs[field]:
                kwargs[field] = _strip_tz(kwargs[field])

        invoice_number = await self.generate_invoice_number()

        invoice = InvoiceFinancing(
            invoice_number=invoice_number,
            invoice_amount=invoice_amount,
            currency=currency,
            invoice_status=InvoiceStatus.DRAFT,
            financing_status=FinancingStatus.NOT_FINANCED,
            created_by=created_by,
            **kwargs,
        )

        db.add(invoice)
        await db.flush()

        # Generate INVOICE_CREATED event
        await self._generate_event(db, "INVOICE_CREATED", invoice, created_by)

        return invoice

    async def get_invoice_by_id(
        self,
        db: AsyncSession,
        invoice_id: int,
    ) -> InvoiceFinancing:
        """Get invoice by ID."""
        result = await db.execute(
            select(InvoiceFinancing).where(InvoiceFinancing.id == invoice_id)
        )
        invoice = result.scalar_one_or_none()

        if not invoice:
            raise NotFoundException(f"Invoice with ID {invoice_id} not found")

        return invoice

    async def list_invoices(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        invoice_status: Optional[InvoiceStatus] = None,
        financing_status: Optional[FinancingStatus] = None,
    ) -> Tuple[List[InvoiceFinancing], int]:
        """List invoices with pagination."""
        query = select(InvoiceFinancing)

        filters = []
        if search:
            filters.append(
                or_(
                    InvoiceFinancing.invoice_number.ilike(f"%{search}%"),
                    InvoiceFinancing.seller_name.ilike(f"%{search}%"),
                    InvoiceFinancing.buyer_name.ilike(f"%{search}%"),
                )
            )
        if invoice_status:
            filters.append(InvoiceFinancing.invoice_status == invoice_status)
        if financing_status:
            filters.append(InvoiceFinancing.financing_status == financing_status)

        if filters:
            query = query.where(and_(*filters))

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0

        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(InvoiceFinancing.created_at.desc())

        result = await db.execute(query)
        invoices = result.scalars().all()

        return list(invoices), total

    async def request_financing(
        self,
        db: AsyncSession,
        invoice_id: int,
        financed_amount: Decimal,
    ) -> InvoiceFinancing:
        """Request financing for invoice."""
        invoice = await self.get_invoice_by_id(db, invoice_id)

        if invoice.financing_status != FinancingStatus.NOT_FINANCED:
            raise BusinessRuleViolationException("Invoice already financed")

        invoice.financing_status = FinancingStatus.FINANCING_REQUESTED
        invoice.financed_amount = financed_amount
        invoice.outstanding_amount = financed_amount

        await db.flush()

        return invoice

    async def approve_financing(
        self,
        db: AsyncSession,
        invoice_id: int,
        user_id: int,
    ) -> InvoiceFinancing:
        """Approve financing."""
        invoice = await self.get_invoice_by_id(db, invoice_id)

        if invoice.financing_status != FinancingStatus.FINANCING_REQUESTED:
            raise BusinessRuleViolationException("Financing not in requested state")

        invoice.financing_status = FinancingStatus.FINANCED
        invoice.financing_start_date = datetime.utcnow()

        await db.flush()

        return invoice

    async def repay_invoice(
        self,
        db: AsyncSession,
        invoice_id: int,
        repayment_amount: Decimal,
    ) -> InvoiceFinancing:
        """Record repayment."""
        invoice = await self.get_invoice_by_id(db, invoice_id)

        if invoice.financing_status != FinancingStatus.FINANCED:
            raise BusinessRuleViolationException("Invoice not financed")

        invoice.repaid_amount = (invoice.repaid_amount or Decimal(0)) + repayment_amount
        invoice.outstanding_amount = invoice.outstanding_amount - repayment_amount

        if invoice.outstanding_amount <= 0:
            invoice.financing_status = FinancingStatus.REPAID
            invoice.invoice_status = InvoiceStatus.PAID

        await db.flush()

        return invoice

    async def update_invoice(
        self,
        db: AsyncSession,
        invoice_id: int,
        invoice_data: dict,
        user_id: int,
    ) -> InvoiceFinancing:
        """Update an invoice."""
        invoice = await self.get_invoice_by_id(db, invoice_id)

        if invoice.invoice_status != InvoiceStatus.DRAFT:
            raise BusinessRuleViolationException("Only draft invoices can be updated")

        # Update allowed fields
        allowed_fields = [
            "invoice_date",
            "due_date",
            "seller_name",
            "seller_address",
            "buyer_name",
            "buyer_address",
            "currency",
            "invoice_amount",
            "internal_reference",
        ]
        for field in allowed_fields:
            if field in invoice_data and invoice_data[field] is not None:
                setattr(invoice, field, invoice_data[field])

        await db.flush()
        audit_logger.log_audit(
            AuditAction.UPDATE,
            user_id,
            f"Invoice {invoice_id} updated",
            {"invoice_id": invoice_id, "fields": list(invoice_data.keys())},
        )

        return invoice

    async def submit_for_approval(
        self,
        db: AsyncSession,
        invoice_id: int,
        user_id: int,
    ) -> InvoiceFinancing:
        """Submit invoice for approval."""
        invoice = await self.get_invoice_by_id(db, invoice_id)

        if invoice.invoice_status != InvoiceStatus.DRAFT:
            raise BusinessRuleViolationException("Only draft invoices can be submitted")

        invoice.invoice_status = InvoiceStatus.SUBMITTED

        await db.flush()
        audit_logger.log_audit(
            AuditAction.UPDATE,
            user_id,
            f"Invoice {invoice_id} submitted for approval",
            {"invoice_id": invoice_id},
        )

        return invoice

    async def approve_invoice(
        self,
        db: AsyncSession,
        invoice_id: int,
        user_id: int,
        remarks: Optional[str] = None,
    ) -> InvoiceFinancing:
        """Approve invoice for financing."""
        invoice = await self.get_invoice_by_id(db, invoice_id)

        if invoice.invoice_status != InvoiceStatus.SUBMITTED:
            raise BusinessRuleViolationException(
                "Only submitted invoices can be approved"
            )

        invoice.invoice_status = InvoiceStatus.APPROVED

        await db.flush()
        audit_logger.log_audit(
            AuditAction.UPDATE,
            user_id,
            f"Invoice {invoice_id} approved",
            {"invoice_id": invoice_id, "remarks": remarks},
        )

        return invoice

    async def reject_invoice(
        self,
        db: AsyncSession,
        invoice_id: int,
        user_id: int,
        reason: str,
    ) -> InvoiceFinancing:
        """Reject invoice."""
        invoice = await self.get_invoice_by_id(db, invoice_id)

        if invoice.invoice_status not in [InvoiceStatus.SUBMITTED, InvoiceStatus.DRAFT]:
            raise BusinessRuleViolationException(
                "Only submitted or draft invoices can be rejected"
            )

        invoice.invoice_status = InvoiceStatus.REJECTED

        await db.flush()
        audit_logger.log_audit(
            AuditAction.UPDATE,
            user_id,
            f"Invoice {invoice_id} rejected",
            {"invoice_id": invoice_id, "reason": reason},
        )

        return invoice

    async def disburse_invoice(
        self,
        db: AsyncSession,
        invoice_id: int,
        user_id: int,
    ) -> InvoiceFinancing:
        """Disburse funds for the invoice."""
        invoice = await self.get_invoice_by_id(db, invoice_id)

        if invoice.invoice_status != InvoiceStatus.APPROVED:
            raise BusinessRuleViolationException(
                "Only approved invoices can be disbursed"
            )

        invoice.financing_status = FinancingStatus.FINANCED
        invoice.financing_start_date = datetime.utcnow()
        invoice.outstanding_amount = invoice.invoice_amount

        await db.flush()
        audit_logger.log_audit(
            AuditAction.UPDATE,
            user_id,
            f"Invoice {invoice_id} disbursed",
            {"invoice_id": invoice_id, "amount": str(invoice.invoice_amount)},
        )

        return invoice

    async def settle_invoice(
        self,
        db: AsyncSession,
        invoice_id: int,
        settlement_amount: float,
        user_id: int,
    ) -> InvoiceFinancing:
        """Settle the invoice."""
        invoice = await self.get_invoice_by_id(db, invoice_id)

        if invoice.financing_status != FinancingStatus.FINANCED:
            raise BusinessRuleViolationException(
                "Only financed invoices can be settled"
            )

        invoice.repaid_amount = (invoice.repaid_amount or Decimal(0)) + Decimal(
            str(settlement_amount)
        )
        invoice.outstanding_amount = (
            invoice.outstanding_amount or Decimal(0)
        ) - Decimal(str(settlement_amount))

        if invoice.outstanding_amount <= 0:
            invoice.financing_status = FinancingStatus.REPAID
            invoice.invoice_status = InvoiceStatus.PAID
            invoice.payment_date = datetime.utcnow()
            invoice.payment_amount = Decimal(str(settlement_amount))

        await db.flush()
        audit_logger.log_audit(
            AuditAction.UPDATE,
            user_id,
            f"Invoice {invoice_id} settled",
            {"invoice_id": invoice_id, "amount": str(settlement_amount)},
        )

        return invoice

    async def cancel_invoice(
        self,
        db: AsyncSession,
        invoice_id: int,
        user_id: int,
        reason: str,
    ) -> InvoiceFinancing:
        """Cancel an invoice."""
        invoice = await self.get_invoice_by_id(db, invoice_id)

        if invoice.invoice_status not in [InvoiceStatus.DRAFT, InvoiceStatus.SUBMITTED]:
            raise BusinessRuleViolationException(
                "Only draft or submitted invoices can be cancelled"
            )

        invoice.invoice_status = InvoiceStatus.CANCELLED

        await db.flush()
        audit_logger.log_audit(
            AuditAction.UPDATE,
            user_id,
            f"Invoice {invoice_id} cancelled",
            {"invoice_id": invoice_id, "reason": reason},
        )

        return invoice


# Singleton instance
invoice_service = InvoiceFinancingService()
