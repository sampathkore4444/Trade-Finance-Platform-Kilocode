"""
Risk Management Router
Handles HTTP endpoints for risk management
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer

from app.database import get_db
from app.core.auth.jwt_handler import get_current_user
from app.modules.risk_management.schemas import (
    RiskAssessmentCreate,
    RiskAssessmentUpdate,
    RiskAssessmentResponse,
    RiskStatus,
    RiskLevel,
)
from app.modules.risk_management.services import RiskManagementService

router = APIRouter(prefix="/risks", tags=["Risk Management"])
security = HTTPBearer()


def get_risk_service(db=Depends(get_db)):
    """Dependency to get risk service"""
    return RiskManagementService(db)


@router.post(
    "/assessment",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_risk_assessment(
    risk_data: RiskAssessmentCreate,
    current_user: dict = Depends(get_current_user),
    service: RiskManagementService = Depends(get_risk_service),
):
    """
    Create a new risk assessment
    """
    risk = await service.create_risk_assessment(
        risk_data=risk_data,
        user_id=current_user["user_id"],
    )
    return risk


@router.get("/", response_model=List[RiskAssessmentResponse])
async def list_risks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[RiskStatus] = None,
    risk_level: Optional[RiskLevel] = None,
    entity_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: RiskManagementService = Depends(get_risk_service),
):
    """
    List all risk assessments with optional filters
    """
    risks = await service.list_risks(
        skip=skip,
        limit=limit,
        status=status,
        risk_level=risk_level,
        entity_type=entity_type,
    )
    return risks


@router.get("/{risk_id}", response_model=RiskAssessmentResponse)
async def get_risk(
    risk_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: RiskManagementService = Depends(get_risk_service),
):
    """
    Get a risk assessment by ID
    """
    risk = await service.get_risk_by_id(risk_id)
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found",
        )
    return risk


@router.put("/{risk_id}", response_model=RiskAssessmentResponse)
async def update_risk(
    risk_id: UUID,
    risk_data: RiskAssessmentUpdate,
    current_user: dict = Depends(get_current_user),
    service: RiskManagementService = Depends(get_risk_service),
):
    """
    Update a risk assessment
    """
    risk = await service.update_risk(
        risk_id=risk_id,
        risk_data=risk_data,
        user_id=current_user["user_id"],
    )
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found",
        )
    return risk


@router.post("/{risk_id}/assess", response_model=RiskAssessmentResponse)
async def assess_risk(
    risk_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: RiskManagementService = Depends(get_risk_service),
):
    """
    Run risk assessment evaluation
    """
    risk = await service.run_risk_assessment(
        risk_id=risk_id,
        user_id=current_user["user_id"],
    )
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found",
        )
    return risk


@router.post("/{risk_id}/approve", response_model=RiskAssessmentResponse)
async def approve_risk(
    risk_id: UUID,
    remarks: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: RiskManagementService = Depends(get_risk_service),
):
    """
    Approve a risk assessment
    """
    risk = await service.approve_risk(
        risk_id=risk_id,
        user_id=current_user["user_id"],
        remarks=remarks,
    )
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found",
        )
    return risk


@router.post("/{risk_id}/reject", response_model=RiskAssessmentResponse)
async def reject_risk(
    risk_id: UUID,
    reason: str,
    current_user: dict = Depends(get_current_user),
    service: RiskManagementService = Depends(get_risk_service),
):
    """
    Reject a risk assessment
    """
    risk = await service.reject_risk(
        risk_id=risk_id,
        user_id=current_user["user_id"],
        reason=reason,
    )
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found",
        )
    return risk


@router.post("/{risk_id}/mitigate", response_model=RiskAssessmentResponse)
async def mitigate_risk(
    risk_id: UUID,
    mitigation_plan: str,
    current_user: dict = Depends(get_current_user),
    service: RiskManagementService = Depends(get_risk_service),
):
    """
    Add mitigation plan to risk
    """
    risk = await service.add_mitigation_plan(
        risk_id=risk_id,
        mitigation_plan=mitigation_plan,
        user_id=current_user["user_id"],
    )
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found",
        )
    return risk


@router.post("/{risk_id}/close", response_model=RiskAssessmentResponse)
async def close_risk(
    risk_id: UUID,
    resolution_notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: RiskManagementService = Depends(get_risk_service),
):
    """
    Close a risk assessment
    """
    risk = await service.close_risk(
        risk_id=risk_id,
        user_id=current_user["user_id"],
        resolution_notes=resolution_notes,
    )
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found",
        )
    return risk


@router.get(
    "/entity/{entity_type}/{entity_id}", response_model=List[RiskAssessmentResponse]
)
async def get_risks_by_entity(
    entity_type: str,
    entity_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: RiskManagementService = Depends(get_risk_service),
):
    """
    Get all risks for a specific entity
    """
    risks = await service.get_risks_by_entity(
        entity_type=entity_type,
        entity_id=entity_id,
    )
    return risks


@router.get("/high-risk/list", response_model=List[RiskAssessmentResponse])
async def get_high_risk_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    service: RiskManagementService = Depends(get_risk_service),
):
    """
    Get all high risk assessments
    """
    risks = await service.get_high_risk_assessments(
        skip=skip,
        limit=limit,
    )
    return risks


@router.get("/pending/list", response_model=List[RiskAssessmentResponse])
async def get_pending_risks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    service: RiskManagementService = Depends(get_risk_service),
):
    """
    Get all pending risk assessments
    """
    risks = await service.get_pending_risks(
        skip=skip,
        limit=limit,
    )
    return risks
