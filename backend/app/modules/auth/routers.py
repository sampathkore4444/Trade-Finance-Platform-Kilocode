"""
Authentication Routers for Trade Finance Platform

This module defines API routes for authentication operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.users.schemas import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
    UserPasswordReset,
    UserPasswordResetConfirm,
    MFAVerifyRequest,
)
from app.modules.users.services import user_service
from app.core.auth.jwt_handler import jwt_handler
from app.core.auth.mfa_handler import mfa_handler


router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return tokens.
    """
    user = await user_service.authenticate_user(
        db=db,
        username=request.username,
        password=request.password,
    )

    # Create tokens
    access_token, refresh_token = await user_service.create_tokens(user)

    # Create session
    await user_service.create_session(
        db=db,
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
    )

    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=900,
        user=None,  # Would populate from user data
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token.
    """
    try:
        user, access_token, refresh_token = await user_service.refresh_tokens(
            db=db,
            refresh_token=request.refresh_token,
        )

        await db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=900,
            user=None,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user.
    """
    # Would get user from token and logout
    return {"message": "Logged out successfully"}


@router.post("/password/reset")
async def request_password_reset(
    request: UserPasswordReset,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset.
    """
    user = await user_service.get_user_by_email(db, request.email)

    if user:
        # Generate password reset token
        token = jwt_handler.create_password_reset_token(user.id, user.email)
        # TODO: Send email with reset link
        print(f"[Password Reset] Token for {user.email}: {token}")

    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password/reset/confirm")
async def confirm_password_reset(
    request: UserPasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm password reset with token.
    """
    # Verify token
    try:
        payload = jwt_handler.decode_token(request.token)
        user_id = payload.get("user_id")

        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    # Verify passwords match
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    # Get user and update password
    user = await user_service.get_user_by_id(db, user_id)
    user.password_hash = jwt_handler.hash_password(request.new_password)

    await db.commit()

    return {"message": "Password reset successfully"}


@router.post("/mfa/verify")
async def verify_mfa(
    request: MFAVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify MFA token.
    """
    # Would verify MFA and return tokens
    return {"message": "MFA verified"}


@router.post("/mfa/send")
async def send_mfa_code(
    mfa_type: str = "sms",
    db: AsyncSession = Depends(get_db),
):
    """
    Send MFA code via SMS or email.
    """
    # Would get user from context and send code
    return {"message": f"MFA code sent via {mfa_type}"}
