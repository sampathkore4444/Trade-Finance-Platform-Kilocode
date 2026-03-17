"""
Auth Schemas for Trade Finance Platform

This module defines Pydantic schemas for authentication operations.
"""

from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    mfa_code: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Optional[dict] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class LogoutRequest(BaseModel):
    """Logout request schema."""

    refresh_token: Optional[str] = None
    all_sessions: bool = False


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""

    email: str = Field(..., format="email")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""

    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class MFAVerifyRequest(BaseModel):
    """MFA verification request schema."""

    token: str
    code: str = Field(..., min_length=6, max_length=6)


class MFASetupResponse(BaseModel):
    """MFA setup response schema."""

    secret: str
    qr_code: str
