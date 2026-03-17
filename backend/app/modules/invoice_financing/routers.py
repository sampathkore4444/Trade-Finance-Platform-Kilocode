"""
Invoice Financing Router
Handles HTTP endpoints for invoice financing
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer

from app.database import get_db
from app.core.auth.jwt_handler import get_current_user
from app.modules.invoice_financing.schemas import (
    InvoiceFinancingCreate,
    InvoiceFinancingUpdate,
    InvoiceFinancingResponse,
    InvoiceStatus,
)
from app.modules.invoice_financing.services import InvoiceFinancingService

router = APIRouter(prefix="/invoices", tags=["Invoice Financing"])
security = HTTPBearer()


def get_invoice_service(db=Depends(get_db)):
    """Dependency to get invoice service"""
    return InvoiceFinancingService(db)


@router.post(
    "/", response_model=InvoiceFinancingResponse, status_code=status.HTTP_201_CREATED
)
async def create_invoice(
    invoice_data: InvoiceFinancingCreate,
    current_user: dict = Depends(get_current_user),
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Create a new invoice for financing
    """
    invoice = await service.create_invoice(
        invoice_data=invoice_data,
        user_id=current_user["user_id"],
    )
    return invoice


@router.get("/", response_model=List[InvoiceFinancingResponse])
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[InvoiceStatus] = None,
    seller_name: Optional[str] = None,
    buyer_name: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    List all invoices with optional filters
    """
    invoices = await service.list_invoices(
        skip=skip,
        limit=limit,
        status=status,
        seller_name=seller_name,
        buyer_name=buyer_name,
    )
    return invoices


@router.get("/{invoice_id}", response_model=InvoiceFinancingResponse)
async def get_invoice(
    invoice_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Get an invoice by ID
    """
    invoice = await service.get_invoice_by_id(invoice_id)
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
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Get an invoice by invoice number
    """
    invoice = await service.get_invoice_by_number(invoice_number)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceFinancingResponse)
async def update_invoice(
    invoice_id: UUID,
    invoice_data: InvoiceFinancingUpdate,
    current_user: dict = Depends(get_current_user),
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Update an invoice
    """
    invoice = await service.update_invoice(
        invoice_id=invoice_id,
        invoice_data=invoice_data,
        user_id=current_user["user_id"],
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.post("/{invoice_id}/submit", response_model=InvoiceFinancingResponse)
async def submit_invoice(
    invoice_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Submit invoice for financing approval
    """
    invoice = await service.submit_for_approval(
        invoice_id=invoice_id,
        user_id=current_user["user_id"],
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.post("/{invoice_id}/approve", response_model=InvoiceFinancingResponse)
async def approve_invoice(
    invoice_id: UUID,
    remarks: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Approve invoice for financing
    """
    invoice = await service.approve_invoice(
        invoice_id=invoice_id,
        user_id=current_user["user_id"],
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
    invoice_id: UUID,
    reason: str,
    current_user: dict = Depends(get_current_user),
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Reject invoice for financing
    """
    invoice = await service.reject_invoice(
        invoice_id=invoice_id,
        user_id=current_user["user_id"],
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
    invoice_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Disburse funds for the invoice
    """
    invoice = await service.disburse_invoice(
        invoice_id=invoice_id,
        user_id=current_user["user_id"],
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.post("/{invoice_id}/settle", response_model=InvoiceFinancingResponse)
async def settle_invoice(
    invoice_id: UUID,
    settlement_amount: float,
    current_user: dict = Depends(get_current_user),
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Settle the invoice
    """
    invoice = await service.settle_invoice(
        invoice_id=invoice_id,
        settlement_amount=settlement_amount,
        user_id=current_user["user_id"],
    )
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.post("/{invoice_id}/cancel", response_model=InvoiceFinancingResponse)
async def cancel_invoice(
    invoice_id: UUID,
    reason: str,
    current_user: dict = Depends(get_current_user),
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Cancel an invoice
    """
    invoice = await service.cancel_invoice(
        invoice_id=invoice_id,
        user_id=current_user["user_id"],
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
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Get invoices by seller account
    """
    invoices = await service.get_invoices_by_seller(
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
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Get invoices by buyer account
    """
    invoices = await service.get_invoices_by_buyer(
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
    service: InvoiceFinancingService = Depends(get_invoice_service),
):
    """
    Get all pending invoices for approval
    """
    invoices = await service.get_pending_invoices(
        skip=skip,
        limit=limit,
    )
    return invoices
