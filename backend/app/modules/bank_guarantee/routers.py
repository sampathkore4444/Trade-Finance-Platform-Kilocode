"""
Bank Guarantee Routers for Trade Finance Platform
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.auth.jwt_handler import get_current_user
from app.modules.bank_guarantee.schemas import (
    BankGuaranteeCreate,
    BankGuaranteeUpdate,
    BankGuaranteeResponse,
)
from app.modules.bank_guarantee.services import guarantee_service

router = APIRouter(tags=["Bank Guarantee"])
security = HTTPBearer()


def get_guarantee_service():
    """Dependency to get guarantee service"""
    return guarantee_service


@router.get("/", response_model=dict)
async def list_guarantees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = None,
    guarantee_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List Bank Guarantees with pagination and filters."""
    service = guarantee_service
    guarantees, total = await service.list_guarantees(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        guarantee_type=guarantee_type,
        status=status,
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    # Convert each guarantee to response schema
    items = [
        BankGuaranteeResponse.model_validate(
            {
                "id": g.id,
                "guarantee_number": g.guarantee_number,
                "guarantee_type": g.guarantee_type,
                "status": g.status,
                "state": g.state,
                "applicant_name": g.applicant_name,
                "applicant_address": g.applicant_address,
                "applicant_country": g.applicant_country,
                "beneficiary_name": g.beneficiary_name,
                "beneficiary_address": g.beneficiary_address,
                "beneficiary_country": g.beneficiary_country,
                "issuing_bank_name": g.issuing_bank_name,
                "issuing_bank_bic": g.issuing_bank_bic,
                "currency": g.currency,
                "amount": g.amount,
                "expiry_date": g.expiry_date,
                "effective_date": g.effective_date,
                "guarantee_terms": g.guarantee_terms,
                "claim_conditions": g.claim_conditions,
                "undertaking_type": g.undertaking_type,
                "is_revokable": g.is_revokable,
                "is_auto_renewal": g.is_auto_renewal,
                "renewal_period_days": g.renewal_period_days,
                "renewal_notice_days": g.renewal_notice_days,
                "internal_reference": g.internal_reference,
                "external_reference": g.external_reference,
                "related_contract_id": g.related_contract_id,
                "applicant_id": g.applicant_id,
                "beneficiary_id": g.beneficiary_id,
                "issuing_bank_id": g.issuing_bank_id,
                "issue_date": g.issue_date,
                "approved_by": g.approved_by,
                "approved_at": g.approved_at,
                "approval_comments": g.approval_comments,
                "rejected_by": g.rejected_by,
                "rejected_at": g.rejected_at,
                "rejection_reason": g.rejection_reason,
                "claimed_by": g.claimed_by,
                "claimed_at": g.claimed_at,
                "claim_amount": g.claim_amount,
                "claim_status": g.claim_status,
                "released_by": g.released_by,
                "released_at": g.released_at,
                "release_amount": g.release_amount,
                "related_lc_id": g.related_lc_id,
                "created_by": g.created_by,
                "assigned_to": g.assigned_to,
                "created_at": g.created_at,
                "updated_at": g.updated_at,
            }
        )
        for g in guarantees
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{guarantee_id}", response_model=BankGuaranteeResponse)
async def get_guarantee(
    guarantee_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a Bank Guarantee by ID."""
    service = guarantee_service
    guarantee = await service.get_guarantee_by_id(db, guarantee_id)
    if not guarantee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guarantee not found",
        )
    return BankGuaranteeResponse.model_validate(
        {
            "id": guarantee.id,
            "guarantee_number": guarantee.guarantee_number,
            "guarantee_type": guarantee.guarantee_type,
            "status": guarantee.status,
            "state": guarantee.state,
            "applicant_name": guarantee.applicant_name,
            "applicant_address": guarantee.applicant_address,
            "applicant_country": guarantee.applicant_country,
            "beneficiary_name": guarantee.beneficiary_name,
            "beneficiary_address": guarantee.beneficiary_address,
            "beneficiary_country": guarantee.beneficiary_country,
            "issuing_bank_name": guarantee.issuing_bank_name,
            "issuing_bank_bic": guarantee.issuing_bank_bic,
            "currency": guarantee.currency,
            "amount": guarantee.amount,
            "expiry_date": guarantee.expiry_date,
            "effective_date": guarantee.effective_date,
            "guarantee_terms": guarantee.guarantee_terms,
            "claim_conditions": guarantee.claim_conditions,
            "undertaking_type": guarantee.undertaking_type,
            "is_revokable": guarantee.is_revokable,
            "is_auto_renewal": guarantee.is_auto_renewal,
            "renewal_period_days": guarantee.renewal_period_days,
            "renewal_notice_days": guarantee.renewal_notice_days,
            "internal_reference": guarantee.internal_reference,
            "external_reference": guarantee.external_reference,
            "related_contract_id": guarantee.related_contract_id,
            "applicant_id": guarantee.applicant_id,
            "beneficiary_id": guarantee.beneficiary_id,
            "issuing_bank_id": guarantee.issuing_bank_id,
            "issue_date": guarantee.issue_date,
            "approved_by": guarantee.approved_by,
            "approved_at": guarantee.approved_at,
            "approval_comments": guarantee.approval_comments,
            "rejected_by": guarantee.rejected_by,
            "rejected_at": guarantee.rejected_at,
            "rejection_reason": guarantee.rejection_reason,
            "claimed_by": guarantee.claimed_by,
            "claimed_at": guarantee.claimed_at,
            "claim_amount": guarantee.claim_amount,
            "claim_status": guarantee.claim_status,
            "released_by": guarantee.released_by,
            "released_at": guarantee.released_at,
            "release_amount": guarantee.release_amount,
            "related_lc_id": guarantee.related_lc_id,
            "created_by": guarantee.created_by,
            "assigned_to": guarantee.assigned_to,
            "created_at": guarantee.created_at,
            "updated_at": guarantee.updated_at,
        }
    )


@router.post(
    "/", response_model=BankGuaranteeResponse, status_code=status.HTTP_201_CREATED
)
async def create_guarantee(
    guarantee_data: BankGuaranteeCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new Bank Guarantee."""
    service = guarantee_service
    guarantee = await service.create_guarantee(
        db=db,
        guarantee_type=guarantee_data.guarantee_type,
        amount=guarantee_data.amount,
        currency=guarantee_data.currency,
        applicant_name=guarantee_data.applicant_name,
        applicant_address=guarantee_data.applicant_address,
        applicant_country=guarantee_data.applicant_country,
        beneficiary_name=guarantee_data.beneficiary_name,
        beneficiary_address=guarantee_data.beneficiary_address,
        beneficiary_country=guarantee_data.beneficiary_country,
        issuing_bank_name=guarantee_data.issuing_bank_name,
        issuing_bank_bic=guarantee_data.issuing_bank_bic,
        expiry_date=guarantee_data.expiry_date,
        effective_date=guarantee_data.effective_date,
        guarantee_terms=guarantee_data.guarantee_terms,
        claim_conditions=guarantee_data.claim_conditions,
        undertaking_type=guarantee_data.undertaking_type,
        is_revokable=guarantee_data.is_revokable,
        is_auto_renewal=guarantee_data.is_auto_renewal,
        renewal_period_days=guarantee_data.renewal_period_days,
        renewal_notice_days=guarantee_data.renewal_notice_days,
        internal_reference=guarantee_data.internal_reference,
        external_reference=guarantee_data.external_reference,
        related_contract_id=guarantee_data.related_contract_id,
        applicant_id=guarantee_data.applicant_id,
        beneficiary_id=guarantee_data.beneficiary_id,
        issuing_bank_id=guarantee_data.issuing_bank_id,
        related_lc_id=guarantee_data.related_lc_id,
        created_by=current_user.id,
    )
    await db.commit()
    await db.refresh(guarantee)
    # Convert to dict first, then validate
    guarantee_dict = {
        "id": guarantee.id,
        "guarantee_number": guarantee.guarantee_number,
        "guarantee_type": guarantee.guarantee_type,
        "status": guarantee.status,
        "state": guarantee.state,
        "applicant_name": guarantee.applicant_name,
        "applicant_address": guarantee.applicant_address,
        "applicant_country": guarantee.applicant_country,
        "beneficiary_name": guarantee.beneficiary_name,
        "beneficiary_address": guarantee.beneficiary_address,
        "beneficiary_country": guarantee.beneficiary_country,
        "issuing_bank_name": guarantee.issuing_bank_name,
        "issuing_bank_bic": guarantee.issuing_bank_bic,
        "currency": guarantee.currency,
        "amount": guarantee.amount,
        "expiry_date": guarantee.expiry_date,
        "effective_date": guarantee.effective_date,
        "guarantee_terms": guarantee.guarantee_terms,
        "claim_conditions": guarantee.claim_conditions,
        "undertaking_type": guarantee.undertaking_type,
        "is_revokable": guarantee.is_revokable,
        "is_auto_renewal": guarantee.is_auto_renewal,
        "renewal_period_days": guarantee.renewal_period_days,
        "renewal_notice_days": guarantee.renewal_notice_days,
        "internal_reference": guarantee.internal_reference,
        "external_reference": guarantee.external_reference,
        "related_contract_id": guarantee.related_contract_id,
        "applicant_id": guarantee.applicant_id,
        "beneficiary_id": guarantee.beneficiary_id,
        "issuing_bank_id": guarantee.issuing_bank_id,
        "issue_date": guarantee.issue_date,
        "approved_by": guarantee.approved_by,
        "approved_at": guarantee.approved_at,
        "approval_comments": guarantee.approval_comments,
        "rejected_by": guarantee.rejected_by,
        "rejected_at": guarantee.rejected_at,
        "rejection_reason": guarantee.rejection_reason,
        "claimed_by": guarantee.claimed_by,
        "claimed_at": guarantee.claimed_at,
        "claim_amount": guarantee.claim_amount,
        "claim_status": guarantee.claim_status,
        "released_by": guarantee.released_by,
        "released_at": guarantee.released_at,
        "release_amount": guarantee.release_amount,
        "related_lc_id": guarantee.related_lc_id,
        "created_by": guarantee.created_by,
        "assigned_to": guarantee.assigned_to,
        "created_at": guarantee.created_at,
        "updated_at": guarantee.updated_at,
    }
    return BankGuaranteeResponse.model_validate(guarantee_dict)


@router.put("/{guarantee_id}", response_model=BankGuaranteeResponse)
async def update_guarantee(
    guarantee_id: int,
    guarantee_data: BankGuaranteeUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a Bank Guarantee."""
    service = guarantee_service
    guarantee = await service.update_guarantee(
        db=db,
        guarantee_id=guarantee_id,
        guarantee_data=guarantee_data,
        user_id=current_user.id,
    )
    if not guarantee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guarantee not found",
        )
    await db.commit()
    await db.refresh(guarantee)
    return BankGuaranteeResponse.model_validate(
        {
            "id": guarantee.id,
            "guarantee_number": guarantee.guarantee_number,
            "guarantee_type": guarantee.guarantee_type,
            "status": guarantee.status,
            "state": guarantee.state,
            "applicant_name": guarantee.applicant_name,
            "applicant_address": guarantee.applicant_address,
            "applicant_country": guarantee.applicant_country,
            "beneficiary_name": guarantee.beneficiary_name,
            "beneficiary_address": guarantee.beneficiary_address,
            "beneficiary_country": guarantee.beneficiary_country,
            "issuing_bank_name": guarantee.issuing_bank_name,
            "issuing_bank_bic": guarantee.issuing_bank_bic,
            "currency": guarantee.currency,
            "amount": guarantee.amount,
            "expiry_date": guarantee.expiry_date,
            "effective_date": guarantee.effective_date,
            "guarantee_terms": guarantee.guarantee_terms,
            "claim_conditions": guarantee.claim_conditions,
            "undertaking_type": guarantee.undertaking_type,
            "is_revokable": guarantee.is_revokable,
            "is_auto_renewal": guarantee.is_auto_renewal,
            "renewal_period_days": guarantee.renewal_period_days,
            "renewal_notice_days": guarantee.renewal_notice_days,
            "internal_reference": guarantee.internal_reference,
            "external_reference": guarantee.external_reference,
            "related_contract_id": guarantee.related_contract_id,
            "applicant_id": guarantee.applicant_id,
            "beneficiary_id": guarantee.beneficiary_id,
            "issuing_bank_id": guarantee.issuing_bank_id,
            "issue_date": guarantee.issue_date,
            "approved_by": guarantee.approved_by,
            "approved_at": guarantee.approved_at,
            "approval_comments": guarantee.approval_comments,
            "rejected_by": guarantee.rejected_by,
            "rejected_at": guarantee.rejected_at,
            "rejection_reason": guarantee.rejection_reason,
            "claimed_by": guarantee.claimed_by,
            "claimed_at": guarantee.claimed_at,
            "claim_amount": guarantee.claim_amount,
            "claim_status": guarantee.claim_status,
            "released_by": guarantee.released_by,
            "released_at": guarantee.released_at,
            "release_amount": guarantee.release_amount,
            "related_lc_id": guarantee.related_lc_id,
            "created_by": guarantee.created_by,
            "assigned_to": guarantee.assigned_to,
            "created_at": guarantee.created_at,
            "updated_at": guarantee.updated_at,
        }
    )


@router.post("/{guarantee_id}/submit", response_model=BankGuaranteeResponse)
async def submit_guarantee(
    guarantee_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit guarantee for approval."""
    service = guarantee_service
    guarantee = await service.submit_guarantee(
        db=db,
        guarantee_id=guarantee_id,
        user_id=current_user.id,
    )
    if not guarantee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guarantee not found",
        )
    return _guarantee_to_response(guarantee)


@router.post("/{guarantee_id}/approve", response_model=BankGuaranteeResponse)
async def approve_guarantee(
    guarantee_id: int,
    remarks: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve guarantee."""
    service = guarantee_service
    guarantee = await service.approve_guarantee(
        db=db,
        guarantee_id=guarantee_id,
        user_id=current_user.id,
        remarks=remarks,
    )
    if not guarantee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guarantee not found",
        )
    return _guarantee_to_response(guarantee)


@router.post("/{guarantee_id}/reject", response_model=BankGuaranteeResponse)
async def reject_guarantee(
    guarantee_id: int,
    reason: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject guarantee."""
    service = guarantee_service
    guarantee = await service.reject_guarantee(
        db=db,
        guarantee_id=guarantee_id,
        user_id=current_user.id,
        reason=reason,
    )
    if not guarantee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guarantee not found",
        )
    return _guarantee_to_response(guarantee)


@router.post("/{guarantee_id}/issue", response_model=BankGuaranteeResponse)
async def issue_guarantee(
    guarantee_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Issue guarantee."""
    service = guarantee_service
    guarantee = await service.issue_guarantee(
        db=db,
        guarantee_id=guarantee_id,
        user_id=current_user.id,
    )
    if not guarantee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guarantee not found",
        )
    return _guarantee_to_response(guarantee)


@router.post("/{guarantee_id}/cancel", response_model=BankGuaranteeResponse)
async def cancel_guarantee(
    guarantee_id: int,
    reason: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel guarantee."""
    service = guarantee_service
    guarantee = await service.cancel_guarantee(
        db=db,
        guarantee_id=guarantee_id,
        user_id=current_user.id,
        reason=reason,
    )
    if not guarantee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guarantee not found",
        )
    return _guarantee_to_response(guarantee)


@router.post("/{guarantee_id}/claim", response_model=BankGuaranteeResponse)
async def claim_guarantee(
    guarantee_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Claim on guarantee."""
    service = guarantee_service
    guarantee = await service.claim_guarantee(
        db=db,
        guarantee_id=guarantee_id,
        user_id=current_user.id,
    )
    if not guarantee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guarantee not found",
        )
    return _guarantee_to_response(guarantee)


@router.post("/{guarantee_id}/release", response_model=BankGuaranteeResponse)
async def release_guarantee(
    guarantee_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Release guarantee."""
    service = guarantee_service
    guarantee = await service.release_guarantee(
        db=db,
        guarantee_id=guarantee_id,
        user_id=current_user.id,
    )
    if not guarantee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guarantee not found",
        )
    return _guarantee_to_response(guarantee)
