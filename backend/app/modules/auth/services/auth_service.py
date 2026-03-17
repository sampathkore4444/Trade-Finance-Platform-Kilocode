"""
Auth Service for Trade Finance Platform

This module contains business logic for authentication operations.
"""

from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import AuthSession
from app.modules.users.models.user import User
from app.modules.users.services.user_service import user_service
from app.core.auth.jwt_handler import jwt_handler
from app.core.auth.mfa_handler import mfa_handler
from app.common.exceptions import (
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.config import settings


class AuthService:
    """Service for authentication-related operations."""

    async def authenticate(
        self,
        db: AsyncSession,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        mfa_code: Optional[str] = None,
    ) -> Tuple[User, str, str]:
        """
        Authenticate user and create tokens.

        Returns:
            Tuple of (user, access_token, refresh_token)
        """
        user = await user_service.authenticate_user(
            db=db,
            username=username,
            password=password,
            ip_address=ip_address,
        )

        # Check MFA if enabled
        if user.mfa_enabled:
            if not mfa_code:
                raise UnauthorizedException(message="MFA code required")
            if not await mfa_handler.verify_code(user=user, code=mfa_code):
                raise UnauthorizedException(message="Invalid MFA code")

        # Create tokens
        access_token, refresh_token = await user_service.create_tokens(user)

        return user, access_token, refresh_token

    async def create_session(
        self,
        db: AsyncSession,
        user_id: int,
        access_token: str,
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthSession:
        """Create authentication session."""
        expires_at = jwt_handler.get_token_expiry(access_token)

        session = AuthSession(
            user_id=user_id,
            session_token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        db.add(session)
        await db.flush()

        return session

    async def refresh_session(
        self,
        db: AsyncSession,
        refresh_token: str,
    ) -> Tuple[User, str, str]:
        """Refresh access token."""
        user, access_token, new_refresh_token = await user_service.refresh_tokens(
            db=db,
            refresh_token=refresh_token,
        )

        return user, access_token, new_refresh_token

    async def logout(
        self,
        db: AsyncSession,
        user_id: int,
        refresh_token: Optional[str] = None,
        all_sessions: bool = False,
    ) -> None:
        """Logout user and invalidate sessions."""
        await user_service.logout(
            db=db,
            user_id=user_id,
            refresh_token=refresh_token,
            all_sessions=all_sessions,
        )

    async def request_password_reset(
        self,
        db: AsyncSession,
        email: str,
    ) -> str:
        """Request password reset."""
        user = await user_service.get_user_by_username(db, email)

        if user:
            token = jwt_handler.create_password_reset_token(user.id, user.email)
            return token

        # Return dummy token for security
        return "dummy_token"

    async def confirm_password_reset(
        self,
        db: AsyncSession,
        token: str,
        new_password: str,
    ) -> None:
        """Confirm password reset."""
        payload = jwt_handler.decode_token(token)

        if payload.get("type") != "password_reset":
            raise ValidationException(message="Invalid token type")

        user_id = payload.get("user_id")
        user = await user_service.get_user_by_id(db, user_id)

        user.password_hash = jwt_handler.hash_password(new_password)
        user.password_changed_at = datetime.utcnow()

        await db.flush()

    async def verify_mfa_setup(
        self,
        db: AsyncSession,
        user_id: int,
        code: str,
    ) -> bool:
        """Verify MFA setup."""
        user = await user_service.get_user_by_id(db, user_id)

        if not user.mfa_secret:
            raise ValidationException(message="MFA not set up")

        return await mfa_handler.verify_code(user=user, code=code)


# Singleton instance
auth_service = AuthService()
