"""
Trade Loan Router
Handles HTTP endpoints for trade loans
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.auth.jwt_handler import get_current_user
from app.modules.users.models import User
from app.modules.trade_loan.schemas import (
    TradeLoanCreate,
    TradeLoanUpdate,
    TradeLoanResponse,
    LoanStatus,
    LoanType,
)
from app.modules.trade_loan.services import trade_loan_service

router = APIRouter(prefix="/loans", tags=["Trade Loan"])
security = HTTPBearer()


def get_loan_service():
    """Dependency to get loan service"""
    return trade_loan_service


@router.post("/", response_model=TradeLoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(
    loan_data: TradeLoanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new trade loan
    """
    loan = await trade_loan_service.create_loan(
        db=db,
        loan_type=loan_data.loan_type,
        principal_amount=loan_data.principal_amount,
        currency=loan_data.currency,
        created_by=current_user.id,
        borrower_name=loan_data.borrower_name,
        start_date=loan_data.start_date,
        end_date=loan_data.end_date,
    )
    return loan


@router.get("/")
async def list_loans(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    status: Optional[LoanStatus] = None,
    loan_type: Optional[LoanType] = None,
    borrower_name: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all trade loans with optional filters
    """
    loans, total = await trade_loan_service.list_loans(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    return {
        "items": loans,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{loan_id}", response_model=TradeLoanResponse)
async def get_loan(
    loan_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a trade loan by ID
    """
    loan = await trade_loan_service.get_loan_by_id(db, loan_id)
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
    db: AsyncSession = Depends(get_db),
):
    """
    Get a trade loan by loan number
    """
    loan = await trade_loan_service.get_loan_by_number(db, loan_number)
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
    db: AsyncSession = Depends(get_db),
):
    """
    Update a trade loan
    """
    loan = await trade_loan_service.update_loan(
        db=db,
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
    loan_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit trade loan for approval
    """
    loan = await trade_loan_service.submit_for_approval(
        db=db,
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
    loan_id: int,
    remarks: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve a trade loan
    """
    loan = await trade_loan_service.approve_loan(
        db=db,
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
    loan_id: int,
    reason: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Reject a trade loan
    """
    loan = await trade_loan_service.reject_loan(
        db=db,
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
    db: AsyncSession = Depends(get_db),
):
    """
    Disburse funds for the loan
    """
    loan = await trade_loan_service.disburse_loan(
        db=db,
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
    db: AsyncSession = Depends(get_db),
):
    """
    Record a loan repayment
    """
    loan = await trade_loan_service.repay_loan(
        db=db,
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
    db: AsyncSession = Depends(get_db),
):
    """
    Settle the loan
    """
    loan = await trade_loan_service.settle_loan(
        db=db,
        loan_id=loan_id,
        user_id=current_user["user_id"],
    )
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )
    return loan


@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan(
    loan_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a trade loan by ID (only draft loans can be deleted)
    """
    try:
        await trade_loan_service.delete_loan(db=db, loan_id=loan_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found",
        )


@router.post("/{loan_id}/cancel", response_model=TradeLoanResponse)
async def cancel_loan(
    loan_id: UUID,
    reason: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel a trade loan
    """
    loan = await trade_loan_service.cancel_loan(
        db=db,
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
    db: AsyncSession = Depends(get_db),
):
    """
    Get loans by borrower account
    """
    loans = await trade_loan_service.get_loans_by_borrower(
        db=db,
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
    db: AsyncSession = Depends(get_db),
):
    """
    Get all pending loans for approval
    """
    loans = await trade_loan_service.get_pending_loans(
        db=db,
        skip=skip,
        limit=limit,
    )
    return loans


@router.get("/active/list", response_model=List[TradeLoanResponse])
async def get_active_loans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all active loans
    """
    loans = await trade_loan_service.get_active_loans(
        db=db,
        skip=skip,
        limit=limit,
    )
    return loans
