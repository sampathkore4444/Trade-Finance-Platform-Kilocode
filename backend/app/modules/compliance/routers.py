"""
Compliance Router
Handles HTTP endpoints for compliance management
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer

from app.database import get_db
from app.core.auth.jwt_handler import get_current_user
from app.modules.compliance.schemas import (
    ComplianceCheckCreate,
    ComplianceCheckUpdate,
    ComplianceCheckResponse,
    ComplianceStatus,
    ComplianceType,
)
from app.modules.compliance.services import ComplianceService

router = APIRouter(prefix="/compliance", tags=["Compliance"])
security = HTTPBearer()


def get_compliance_service(db=Depends(get_db)):
    """Dependency to get compliance service"""
    return ComplianceService(db)


@router.post(
    "/check",
    response_model=ComplianceCheckResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_compliance_check(
    check_data: ComplianceCheckCreate,
    current_user: dict = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
):
    """
    Create a new compliance check
    """
    compliance = await service.create_compliance_check(
        check_data=check_data,
        user_id=current_user["user_id"],
    )
    return compliance


@router.get("/", response_model=List[ComplianceCheckResponse])
async def list_compliance_checks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[ComplianceStatus] = None,
    compliance_type: Optional[ComplianceType] = None,
    entity_name: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
):
    """
    List all compliance checks with optional filters
    """
    checks = await service.list_compliance_checks(
        skip=skip,
        limit=limit,
        status=status,
        compliance_type=compliance_type,
        entity_name=entity_name,
    )
    return checks


@router.get("/{check_id}", response_model=ComplianceCheckResponse)
async def get_compliance_check(
    check_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
):
    """
    Get a compliance check by ID
    """
    compliance = await service.get_compliance_by_id(check_id)
    if not compliance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance check not found",
        )
    return compliance


@router.put("/{check_id}", response_model=ComplianceCheckResponse)
async def update_compliance_check(
    check_id: UUID,
    check_data: ComplianceCheckUpdate,
    current_user: dict = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
):
    """
    Update a compliance check
    """
    compliance = await service.update_compliance_check(
        check_id=check_id,
        check_data=check_data,
        user_id=current_user["user_id"],
    )
    if not compliance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance check not found",
        )
    return compliance


@router.post("/{check_id}/run", response_model=ComplianceCheckResponse)
async def run_compliance_check(
    check_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
):
    """
    Run compliance check evaluation
    """
    compliance = await service.run_compliance_check(
        check_id=check_id,
        user_id=current_user["user_id"],
    )
    if not compliance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance check not found",
        )
    return compliance


@router.post("/{check_id}/approve", response_model=ComplianceCheckResponse)
async def approve_compliance(
    check_id: UUID,
    remarks: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
):
    """
    Approve a compliance check
    """
    compliance = await service.approve_compliance(
        check_id=check_id,
        user_id=current_user["user_id"],
        remarks=remarks,
    )
    if not compliance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance check not found",
        )
    return compliance


@router.post("/{check_id}/reject", response_model=ComplianceCheckResponse)
async def reject_compliance(
    check_id: UUID,
    reason: str,
    current_user: dict = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
):
    """
    Reject a compliance check
    """
    compliance = await service.reject_compliance(
        check_id=check_id,
        user_id=current_user["user_id"],
        reason=reason,
    )
    if not compliance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance check not found",
        )
    return compliance


@router.post("/{check_id}/waive", response_model=ComplianceCheckResponse)
async def waive_compliance(
    check_id: UUID,
    waiver_reason: str,
    current_user: dict = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
):
    """
    Waive a compliance check
    """
    compliance = await service.waive_compliance(
        check_id=check_id,
        waiver_reason=waiver_reason,
        user_id=current_user["user_id"],
    )
    if not compliance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance check not found",
        )
    return compliance


@router.get(
    "/entity/{entity_type}/{entity_id}", response_model=List[ComplianceCheckResponse]
)
async def get_compliance_by_entity(
    entity_type: str,
    entity_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
):
    """
    Get all compliance checks for a specific entity
    """
    checks = await service.get_compliance_by_entity(
        entity_type=entity_type,
        entity_id=entity_id,
    )
    return checks


@router.get("/failed/list", response_model=List[ComplianceCheckResponse])
async def get_failed_compliance_checks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
):
    """
    Get all failed compliance checks
    """
    checks = await service.get_failed_checks(
        skip=skip,
        limit=limit,
    )
    return checks


@router.get("/pending/list", response_model=List[ComplianceCheckResponse])
async def get_pending_compliance_checks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    service: ComplianceService = Depends(get_compliance_service),
):
    """
    Get all pending compliance checks
    """
    checks = await service.get_pending_checks(
        skip=skip,
        limit=limit,
    )
    return checks
