"""
Bank Guarantee Routers for Trade Finance Platform
"""

from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/")
async def list_guarantees():
    """List Bank Guarantees."""
    return {"items": [], "total": 0}
