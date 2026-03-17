"""
Documentary Collection Router
Handles HTTP endpoints for documentary collections
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.database import get_db
from app.core.auth.jwt_handler import get_current_user
from app.modules.documentary_collection.schemas import (
    DocumentaryCollectionCreate,
    DocumentaryCollectionUpdate,
    DocumentaryCollectionResponse,
)
from app.modules.documentary_collection.models import CollectionStatus
from app.modules.documentary_collection.services import DocumentaryCollectionService

router = APIRouter(prefix="/collections", tags=["Documentary Collection"])
security = HTTPBearer()


class PaginatedCollectionResponse(BaseModel):
    items: List[DocumentaryCollectionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


async def get_collection_service(db=Depends(get_db)):
    """Dependency to get collection service"""
    return DocumentaryCollectionService(db)


@router.post(
    "/",
    response_model=DocumentaryCollectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_collection(
    collection_data: DocumentaryCollectionCreate,
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Create a new documentary collection
    """
    collection = await service.create_collection(
        collection_data=collection_data,
        user_id=current_user["user_id"],
    )
    return collection


@router.get("/", response_model=PaginatedCollectionResponse)
async def list_collections(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[CollectionStatus] = None,
    search: Optional[str] = None,
    collection_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    List all documentary collections with optional filters and pagination
    """
    # Calculate skip value from page
    skip = (page - 1) * page_size
    
    # Get total count
    total = await service.count_collections(
        status=status,
        search=search,
        collection_type=collection_type,
    )
    
    collections = await service.list_collections(
        skip=skip,
        limit=page_size,
        status=status,
        search=search,
        collection_type=collection_type,
    )
    
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    return {
        "items": collections,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{collection_id}", response_model=DocumentaryCollectionResponse)
async def get_collection(
    collection_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Get a documentary collection by ID
    """
    collection = await service.get_collection_by_id(collection_id)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )
    return collection


@router.get("/number/{collection_number}", response_model=DocumentaryCollectionResponse)
async def get_collection_by_number(
    collection_number: str,
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Get a documentary collection by collection number
    """
    collection = await service.get_collection_by_number(collection_number)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )
    return collection


@router.put("/{collection_id}", response_model=DocumentaryCollectionResponse)
async def update_collection(
    collection_id: UUID,
    collection_data: DocumentaryCollectionUpdate,
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Update a documentary collection
    """
    collection = await service.update_collection(
        collection_id=collection_id,
        collection_data=collection_data,
        user_id=current_user["user_id"],
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )
    return collection


@router.post("/{collection_id}/submit", response_model=DocumentaryCollectionResponse)
async def submit_collection(
    collection_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Submit documentary collection for approval
    """
    collection = await service.submit_for_approval(
        collection_id=collection_id,
        user_id=current_user["user_id"],
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )
    return collection


@router.post("/{collection_id}/approve", response_model=DocumentaryCollectionResponse)
async def approve_collection(
    collection_id: UUID,
    remarks: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Approve a documentary collection
    """
    collection = await service.approve_collection(
        collection_id=collection_id,
        user_id=current_user["user_id"],
        remarks=remarks,
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )
    return collection


@router.post("/{collection_id}/reject", response_model=DocumentaryCollectionResponse)
async def reject_collection(
    collection_id: UUID,
    reason: str,
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Reject a documentary collection
    """
    collection = await service.reject_collection(
        collection_id=collection_id,
        user_id=current_user["user_id"],
        reason=reason,
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )
    return collection


@router.post("/{collection_id}/process", response_model=DocumentaryCollectionResponse)
async def process_collection(
    collection_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Process the documentary collection
    """
    collection = await service.process_collection(
        collection_id=collection_id,
        user_id=current_user["user_id"],
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )
    return collection


@router.post("/{collection_id}/complete", response_model=DocumentaryCollectionResponse)
async def complete_collection(
    collection_id: UUID,
    final_amount: Optional[float] = None,
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Complete a documentary collection
    """
    collection = await service.complete_collection(
        collection_id=collection_id,
        user_id=current_user["user_id"],
        final_amount=final_amount,
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )
    return collection


@router.post("/{collection_id}/cancel", response_model=DocumentaryCollectionResponse)
async def cancel_collection(
    collection_id: UUID,
    reason: str,
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Cancel a documentary collection
    """
    collection = await service.cancel_collection(
        collection_id=collection_id,
        user_id=current_user["user_id"],
        reason=reason,
    )
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )
    return collection


@router.get("/applicant/{account}", response_model=List[DocumentaryCollectionResponse])
async def get_collections_by_applicant(
    account: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Get collections by applicant account
    """
    collections = await service.get_collections_by_applicant(
        applicant_account=account,
        skip=skip,
        limit=limit,
    )
    return collections


@router.get(
    "/beneficiary/{account}", response_model=List[DocumentaryCollectionResponse]
)
async def get_collections_by_beneficiary(
    account: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Get collections by beneficiary account
    """
    collections = await service.get_collections_by_beneficiary(
        beneficiary_account=account,
        skip=skip,
        limit=limit,
    )
    return collections


@router.get("/pending/list", response_model=List[DocumentaryCollectionResponse])
async def get_pending_collections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    service: DocumentaryCollectionService = Depends(get_collection_service),
):
    """
    Get all pending collections for approval
    """
    collections = await service.get_pending_collections(
        skip=skip,
        limit=limit,
    )
    return collections
