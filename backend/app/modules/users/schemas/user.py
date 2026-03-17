"""
User Schemas for Trade Finance Platform
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum


class UserStatusEnum(str, Enum):
    """User status enumeration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    LOCKED = "locked"


class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    phone_country_code: Optional[str] = Field(None, max_length=5)


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, max_length=100)
    organization_id: Optional[int] = None
    branch_id: Optional[int] = None
    department_id: Optional[int] = None
    role_ids: List[int] = []


class UserUpdate(BaseModel):
    """User update schema."""

    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    phone_country_code: Optional[str] = Field(None, max_length=5)
    organization_id: Optional[int] = None
    branch_id: Optional[int] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""

    id: int
    full_name: Optional[str]
    status: UserStatusEnum
    is_active: bool
    is_verified: bool
    is_mfa_enabled: bool
    failed_login_attempts: int
    last_login_at: Optional[datetime]
    locked_until: Optional[datetime]
    organization_id: Optional[int]
    branch_id: Optional[int]
    department_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(BaseModel):
    """User profile response schema."""

    id: int
    username: str
    email: str
    full_name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    phone_country_code: Optional[str]
    organization_id: Optional[int]
    branch_id: Optional[int]
    department_id: Optional[int]
    is_mfa_enabled: bool
    last_login_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """User list response schema."""

    items: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    remember_me: bool = False


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Optional[UserProfileResponse] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request schema."""

    refresh_token: Optional[str] = None
    all_sessions: bool = False


class UserPasswordReset(BaseModel):
    """User password reset request schema."""

    email: EmailStr


class UserPasswordResetConfirm(BaseModel):
    """User password reset confirmation schema."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class MFAVerifyRequest(BaseModel):
    """MFA verification request schema."""

    user_id: int
    code: str = Field(..., min_length=6, max_length=6)
