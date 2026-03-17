"""
Bank Guarantee Routers for Trade Finance Platform
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from app.database import get_db
from app.core.auth.jwt_handler import get_current_user

router = APIRouter(tags=["Bank Guarantee"])


class GuaranteeResponse(BaseModel):
    id: int
    guarantee_number: str
    guarantee_type: str
    status: str
    state: str
    applicant_name: str
    beneficiary_name: str
    currency: str
    amount: float
    expiry_date: Optional[str] = None
    created_at: str


class PaginatedGuaranteeResponse(BaseModel):
    items: List[GuaranteeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# In-memory storage for demo purposes
guarantees_db = []


@router.get("/", response_model=PaginatedGuaranteeResponse)
async def list_guarantees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = None,
    guarantee_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """List Bank Guarantees with pagination and filters."""
    # Filter guarantees based on search and type
    filtered = guarantees_db
    
    if search:
        search_lower = search.lower()
        filtered = [
            g for g in filtered
            if search_lower in g["guarantee_number"].lower()
            or search_lower in g["applicant_name"].lower()
            or search_lower in g["beneficiary_name"].lower()
        ]
    
    if guarantee_type:
        filtered = [g for g in filtered if g["guarantee_type"] == guarantee_type]
    
    if status:
        filtered = [g for g in filtered if g["status"] == status]
    
    total = len(filtered)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    # Paginate
    skip = (page - 1) * page_size
    paginated_items = filtered[skip:skip + page_size]
    
    return {
        "items": paginated_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{guarantee_id}", response_model=GuaranteeResponse)
async def get_guarantee(
    guarantee_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Get a Bank Guarantee by ID."""
    for g in guarantees_db:
        if g["id"] == guarantee_id:
            return g
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Guarantee not found",
    )


@router.post("/", response_model=GuaranteeResponse, status_code=status.HTTP_201_CREATED)
async def create_guarantee(
    guarantee_data: dict,
    current_user: dict = Depends(get_current_user),
):
    """Create a new Bank Guarantee."""
    new_guarantee = {
        "id": len(guarantees_db) + 1,
        "guarantee_number": f"BG-{len(guarantees_db) + 1:06d}",
        "guarantee_type": guarantee_data.get("guarantee_type", "performance_bond"),
        "status": "draft",
        "state": "draft",
        "applicant_name": guarantee_data.get("applicant_name", ""),
        "beneficiary_name": guarantee_data.get("beneficiary_name", ""),
        "currency": guarantee_data.get("currency", "USD"),
        "amount": guarantee_data.get("amount", 0),
        "expiry_date": guarantee_data.get("expiry_date"),
        "created_at": "2024-01-01T00:00:00Z",
    }
    guarantees_db.append(new_guarantee)
    return new_guarantee
