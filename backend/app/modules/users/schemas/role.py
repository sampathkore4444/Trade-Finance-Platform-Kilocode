"""
Role Schemas for Trade Finance Platform
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class RoleBase(BaseModel):
    """Base role schema."""

    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class RoleCreate(RoleBase):
    """Role creation schema."""

    permission_ids: List[int] = []


class RoleUpdate(RoleBase):
    """Role update schema."""

    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    """Role response schema."""

    id: int
    is_system_role: bool
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PermissionResponse(BaseModel):
    """Permission response schema."""

    id: int
    name: str
    description: Optional[str]
    resource: Optional[str]
    action: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserRolesUpdate(BaseModel):
    """User roles update schema."""

    role_ids: List[int]
