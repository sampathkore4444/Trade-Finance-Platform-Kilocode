"""
Letter of Credit Routers for Trade Finance Platform

This module defines API routes for LC operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from decimal import Decimal

from app.database import get_db
from app.modules.letter_of_credit.schemas import (
    LetterOfCreditCreate,
    LetterOfCreditUpdate,
    LetterOfCreditResponse,
    LetterOfCreditApprove,
    LetterOfCreditReject,
    LCListResponse,
    LCAmendmentCreate,
    LCAmendmentResponse,
    LCDocumentCreate,
    LCDocumentResponse,
)
from app.modules.letter_of_credit.services import lc_service
from app.modules.letter_of_credit.models import LCType, LCStatus
from app.core.auth.jwt_handler import jwt_handler
from app.core.auth.rbac_handler import rbac_handler, Permission
from app.common.exceptions import NotFoundException, BusinessRuleViolationException


router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Get current authenticated user from JWT token.
    """
    token = credentials.credentials
    payload = jwt_handler.decode_token(token)
    return {
        "user_id": payload.get("user_id"),
        "username": payload.get("sub"),
        "roles": payload.get("roles", []),
        "permissions": payload.get("permissions", []),
    }


@router.get("/", response_model=LCListResponse)
async def list_lcs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    lc_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List Letters of Credit with pagination.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.LC_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    # Convert status string to enum
    status_enum = LCStatus[status.upper()] if status else None
    type_enum = LCType[lc_type.upper()] if lc_type else None

    lcs, total = await lc_service.list_lcs(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        status=status_enum,
        lc_type=type_enum,
    )

    total_pages = (total + page_size - 1) // page_size

    return LCListResponse(
        items=[LetterOfCreditResponse.model_validate(lc) for lc in lcs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post(
    "/", response_model=LetterOfCreditResponse, status_code=status.HTTP_201_CREATED
)
async def create_lc(
    lc_data: LetterOfCreditCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new Letter of Credit.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.LC_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    lc = await lc_service.create_lc(
        db=db,
        lc_type=lc_data.lc_type,
        amount=lc_data.amount,
        currency=lc_data.currency,
        created_by=current_user["user_id"],
        **lc_data.model_dump(
            exclude_unset=True, exclude={"lc_type", "amount", "currency"}
        ),
    )

    await db.commit()

    return LetterOfCreditResponse.model_validate(lc)


@router.get("/{lc_id}", response_model=LetterOfCreditResponse)
async def get_lc(
    lc_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get Letter of Credit by ID.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.LC_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    try:
        lc = await lc_service.get_lc_by_id(db, lc_id)
        return LetterOfCreditResponse.model_validate(lc)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{lc_id}", response_model=LetterOfCreditResponse)
async def update_lc(
    lc_id: int,
    lc_data: LetterOfCreditUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update Letter of Credit.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.LC_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    try:
        lc = await lc_service.update_lc(
            db=db,
            lc_id=lc_id,
            user_id=current_user["user_id"],
            **lc_data.model_dump(exclude_unset=True),
        )
        await db.commit()
        return LetterOfCreditResponse.model_validate(lc)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{lc_id}/submit", response_model=LetterOfCreditResponse)
async def submit_lc(
    lc_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit LC for approval.
    """
    try:
        lc = await lc_service.submit_lc(
            db=db,
            lc_id=lc_id,
            user_id=current_user["user_id"],
        )
        await db.commit()
        return LetterOfCreditResponse.model_validate(lc)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{lc_id}/approve", response_model=LetterOfCreditResponse)
async def approve_lc(
    lc_id: int,
    data: LetterOfCreditApprove,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve Letter of Credit.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.LC_APPROVE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    try:
        lc = await lc_service.approve_lc(
            db=db,
            lc_id=lc_id,
            user_id=current_user["user_id"],
            comments=data.comments,
        )
        await db.commit()
        return LetterOfCreditResponse.model_validate(lc)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{lc_id}/reject", response_model=LetterOfCreditResponse)
async def reject_lc(
    lc_id: int,
    data: LetterOfCreditReject,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Reject Letter of Credit.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.LC_APPROVE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    try:
        lc = await lc_service.reject_lc(
            db=db,
            lc_id=lc_id,
            user_id=current_user["user_id"],
            reason=data.reason,
        )
        await db.commit()
        return LetterOfCreditResponse.model_validate(lc)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{lc_id}/issue", response_model=LetterOfCreditResponse)
async def issue_lc(
    lc_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Issue Letter of Credit.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.LC_APPROVE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    try:
        lc = await lc_service.issue_lc(
            db=db,
            lc_id=lc_id,
            user_id=current_user["user_id"],
        )
        await db.commit()
        return LetterOfCreditResponse.model_validate(lc)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{lc_id}/amend",
    response_model=LCAmendmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_amendment(
    lc_id: int,
    data: LCAmendmentCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create LC amendment.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.LC_AMEND):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    try:
        amendment = await lc_service.create_amendment(
            db=db,
            lc_id=lc_id,
            user_id=current_user["user_id"],
            **data.model_dump(),
        )
        await db.commit()
        return LCAmendmentResponse.model_validate(amendment)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{lc_id}/documents",
    response_model=LCDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_document(
    lc_id: int,
    data: LCDocumentCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add document to LC.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.LC_DOCUMENTS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    try:
        document = await lc_service.add_document(
            db=db,
            lc_id=lc_id,
            document_type=data.document_type.value,
            document_name=data.document_name,
            **data.model_dump(exclude_unset=True),
        )
        await db.commit()
        return LCDocumentResponse.model_validate(document)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{lc_id}/payment", response_model=LetterOfCreditResponse)
async def process_payment(
    lc_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Process LC payment.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.LC_PAYMENT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    try:
        lc = await lc_service.process_payment(
            db=db,
            lc_id=lc_id,
            user_id=current_user["user_id"],
        )
        await db.commit()
        return LetterOfCreditResponse.model_validate(lc)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{lc_id}/close", response_model=LetterOfCreditResponse)
async def close_lc(
    lc_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Close Letter of Credit.
    """
    try:
        lc = await lc_service.close_lc(
            db=db,
            lc_id=lc_id,
            user_id=current_user["user_id"],
        )
        await db.commit()
        return LetterOfCreditResponse.model_validate(lc)
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleViolationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
