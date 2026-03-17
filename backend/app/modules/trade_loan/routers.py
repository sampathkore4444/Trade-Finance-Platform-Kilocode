"""
Trade Loan Router
Handles HTTP endpoints for trade loans
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer

from app.database import get_db
from app.core.auth.jwt_handler import get_current_user
from app.modules.trade_loan.schemas import (
    TradeLoanCreate,
    TradeLoanUpdate,
    TradeLoanResponse,
    LoanStatus,
    LoanType,
)
from app.modules.trade_loan.services import TradeLoanService

router = APIRouter(prefix="/loans", tags=["Trade Loan"])
security = HTTPBearer()


def get_loan_service(db=Depends(get_db)):
    """Dependency to get loan service"""
    return TradeLoanService(db)


@router.post("/", response_model=TradeLoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(
    loan_data: TradeLoanCreate,
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Create a new trade loan
    """
    loan = await service.create_loan(
        loan_data=loan_data,
        user_id=current_user["user_id"],
    )
    return loan


@router.get("/", response_model=List[TradeLoanResponse])
async def list_loans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[LoanStatus] = None,
    loan_type: Optional[LoanType] = None,
    borrower_name: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    List all trade loans with optional filters
    """
    loans = await service.list_loans(
        skip=skip,
        limit=limit,
        status=status,
        loan_type=loan_type,
        borrower_name=borrower_name,
    )
    return loans


@router.get("/{loan_id}", response_model=TradeLoanResponse)
async def get_loan(
    loan_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Get a trade loan by ID
    """
    loan = await service.get_loan_by_id(loan_id)
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )
    return loan


@router.get("/number/{loan_number}", response_model=TradeLoanResponse)
async def get_loan_by_number(
    loan_number: str,
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Get a trade loan by loan number
    """
    loan = await service.get_loan_by_number(loan_number)
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )
    return loan


@router.put("/{loan_id}", response_model=TradeLoanResponse)
async def update_loan(
    loan_id: UUID,
    loan_data: TradeLoanUpdate,
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Update a trade loan
    """
    loan = await service.update_loan(
        loan_id=loan_id,
        loan_data=loan_data,
        user_id=current_user["user_id"],
    )
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )
    return loan


@router.post("/{loan_id}/submit", response_model=TradeLoanResponse)
async def submit_loan(
    loan_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Submit trade loan for approval
    """
    loan = await service.submit_for_approval(
        loan_id=loan_id,
        user_id=current_user["user_id"],
    )
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )
    return loan


@router.post("/{loan_id}/approve", response_model=TradeLoanResponse)
async def approve_loan(
    loan_id: UUID,
    remarks: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Approve a trade loan
    """
    loan = await service.approve_loan(
        loan_id=loan_id,
        user_id=current_user["user_id"],
        remarks=remarks,
    )
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )
    return loan


@router.post("/{loan_id}/reject", response_model=TradeLoanResponse)
async def reject_loan(
    loan_id: UUID,
    reason: str,
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Reject a trade loan
    """
    loan = await service.reject_loan(
        loan_id=loan_id,
        user_id=current_user["user_id"],
        reason=reason,
    )
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )
    return loan


@router.post("/{loan_id}/disburse", response_model=TradeLoanResponse)
async def disburse_loan(
    loan_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Disburse funds for the loan
    """
    loan = await service.disburse_loan(
        loan_id=loan_id,
        user_id=current_user["user_id"],
    )
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )
    return loan


@router.post("/{loan_id}/repay", response_model=TradeLoanResponse)
async def repay_loan(
    loan_id: UUID,
    amount: float,
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Record a loan repayment
    """
    loan = await service.repay_loan(
        loan_id=loan_id,
        amount=amount,
        user_id=current_user["user_id"],
    )
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )
    return loan


@router.post("/{loan_id}/settle", response_model=TradeLoanResponse)
async def settle_loan(
    loan_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Settle the loan
    """
    loan = await service.settle_loan(
        loan_id=loan_id,
        user_id=current_user["user_id"],
    )
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )
    return loan


@router.post("/{loan_id}/cancel", response_model=TradeLoanResponse)
async def cancel_loan(
    loan_id: UUID,
    reason: str,
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Cancel a trade loan
    """
    loan = await service.cancel_loan(
        loan_id=loan_id,
        user_id=current_user["user_id"],
        reason=reason,
    )
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )
    return loan


@router.get("/borrower/{account}", response_model=List[TradeLoanResponse])
async def get_loans_by_borrower(
    account: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Get loans by borrower account
    """
    loans = await service.get_loans_by_borrower(
        borrower_account=account,
        skip=skip,
        limit=limit,
    )
    return loans


@router.get("/pending/list", response_model=List[TradeLoanResponse])
async def get_pending_loans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Get all pending loans for approval
    """
    loans = await service.get_pending_loans(
        skip=skip,
        limit=limit,
    )
    return loans


@router.get("/active/list", response_model=List[TradeLoanResponse])
async def get_active_loans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    service: TradeLoanService = Depends(get_loan_service),
):
    """
    Get all active loans
    """
    loans = await service.get_active_loans(
        skip=skip,
        limit=limit,
    )
    return loans
