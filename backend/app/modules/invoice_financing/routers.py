"""
Invoice Financing Router
Handles HTTP endpoints for invoice financing
"""

from uuid import UUID
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.auth.jwt_handler import get_current_user
from app.modules.invoice_financing.schemas import (
    InvoiceFinancingCreate,
    InvoiceFinancingUpdate,
    InvoiceFinancingResponse,
    InvoiceStatus,
)
from app.modules.invoice_financing.services import invoice_service

router = APIRouter(prefix="/invoices", tags=["Invoice Financing"])
security = HTTPBearer()


def get_invoice_service():
    """Dependency to get invoice service"""
    return invoice_service


@router.post(
    "/", response_model=InvoiceFinancingResponse, status_code=status.HTTP_201_CREATED
)
async def create_invoice(
    invoice_data: InvoiceFinancingCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new invoice for financing
    """
    invoice = await invoice_service.create_invoice(
        db=db,
        invoice_amount=invoice_data.invoice_amount,
        currency=invoice_data.currency,
        created_by=current_user.id,
        seller_name=invoice_data.seller_name,
        seller_address=invoice_data.seller_address,
        buyer_name=invoice_data.buyer_name,
        buyer_address=invoice_data.buyer_address,
    )
    return invoice


@router.get("/")
async def list_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    status: Optional[str] = None,
    seller_name: Optional[str] = None,
    buyer_name: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all invoices with optional filters
    """
    # Convert status string to InvoiceStatus enum if provided
    invoice_status = None
    if status:
        try:
            invoice_status = InvoiceStatus(status)
        except ValueError:
            pass

    invoices, total = await invoice_service.list_invoices(
        db=db,
        page=page,
        page_size=page_size,
        search=None,
        invoice_status=invoice_status,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    return {
        "items": invoices,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{invoice_id}", response_model=InvoiceFinancingResponse)
async def get_invoice(
    invoice_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get an invoice by ID
    """
    invoice = await invoice_service.get_invoice_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.get("/number/{invoice_number}", response_model=InvoiceFinancingResponse)
async def get_invoice_by_number(
    invoice_number: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get an invoice by invoice number
    """
    invoice = await invoice_service.get_invoice_by_number(db, invoice_number)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceFinancingResponse)
async def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceFinancingUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an invoice
    """
    invoice = await invoice_service.update_invoice(
        db=db,
        invoice_id=invoice_id,
        invoice_data=invoice_data,
        user_id=current_user.id,
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.post("/{invoice_id}/submit", response_model=InvoiceFinancingResponse)
async def submit_invoice(
    invoice_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit invoice for financing approval
    """
    invoice = await invoice_service.submit_for_approval(
        db=db,
        invoice_id=invoice_id,
        user_id=current_user.id,
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.post("/{invoice_id}/approve", response_model=InvoiceFinancingResponse)
async def approve_invoice(
    invoice_id: int,
    remarks: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve invoice for financing
    """
    invoice = await invoice_service.approve_invoice(
        db=db,
        invoice_id=invoice_id,
        user_id=current_user.id,
        remarks=remarks,
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.post("/{invoice_id}/reject", response_model=InvoiceFinancingResponse)
async def reject_invoice(
    invoice_id: int,
    reason: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Reject invoice for financing
    """
    invoice = await invoice_service.reject_invoice(
        db=db,
        invoice_id=invoice_id,
        user_id=current_user.id,
        reason=reason,
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.post("/{invoice_id}/disburse", response_model=InvoiceFinancingResponse)
async def disburse_invoice(
    invoice_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disburse funds for the invoice
    """
    invoice = await invoice_service.disburse_invoice(
        db=db,
        invoice_id=invoice_id,
        user_id=current_user.id,
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.post("/{invoice_id}/settle", response_model=InvoiceFinancingResponse)
async def settle_invoice(
    invoice_id: int,
    settlement_amount: float,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Settle the invoice
    """
    invoice = await invoice_service.settle_invoice(
        db=db,
        invoice_id=invoice_id,
        settlement_amount=settlement_amount,
        user_id=current_user.id,
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.post("/{invoice_id}/cancel", response_model=InvoiceFinancingResponse)
async def cancel_invoice(
    invoice_id: int,
    reason: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel an invoice
    """
    invoice = await invoice_service.cancel_invoice(
        db=db,
        invoice_id=invoice_id,
        user_id=current_user.id,
        reason=reason,
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.get("/seller/{account}", response_model=List[InvoiceFinancingResponse])
async def get_invoices_by_seller(
    account: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get invoices by seller account
    """
    invoices = await invoice_service.get_invoices_by_seller(
        db=db,
        seller_account=account,
        skip=skip,
        limit=limit,
    )
    return invoices


@router.get("/buyer/{account}", response_model=List[InvoiceFinancingResponse])
async def get_invoices_by_buyer(
    account: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get invoices by buyer account
    """
    invoices = await invoice_service.get_invoices_by_buyer(
        db=db,
        buyer_account=account,
        skip=skip,
        limit=limit,
    )
    return invoices


@router.get("/pending/list", response_model=List[InvoiceFinancingResponse])
async def get_pending_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all pending invoices for approval
    """
    invoices = await invoice_service.get_pending_invoices(
        db=db,
        skip=skip,
        limit=limit,
    )
    return invoices
