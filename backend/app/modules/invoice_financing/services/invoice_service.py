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


class InvoiceFinancingService:
    """Service for Invoice Financing operations."""

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


# Singleton instance
invoice_service = InvoiceFinancingService()
