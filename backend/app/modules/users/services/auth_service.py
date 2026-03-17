"""
Authentication Service for Trade Finance Platform

This module contains business logic for authentication operations.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models.user import User, UserStatus
from app.modules.users.models.session import UserSession
from app.modules.users.services.user_service import user_service
from app.core.auth.mfa_handler import mfa_handler
from app.core.auth.jwt_handler import jwt_handler
from app.core.security.audit_logger import audit_logger, AuditAction
from app.common.exceptions import (
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ValidationException,
)
from app.config import settings


class AuthService:
    """Service for authentication-related operations."""

    async def login(
        self,
        db: AsyncSession,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        mfa_code: Optional[str] = None,
    ) -> dict:
        """
        Authenticate user and create session.

        Returns access token, refresh token, and user info.
        """
        user = await user_service.authenticate_user(
            db=db,
            username=username,
            password=password,
            ip_address=ip_address,
        )

        # Check if MFA is required
        if user.mfa_enabled:
            if not mfa_code:
                # Return partial success - need MFA
                return {
                    "requires_mfa": True,
                    "mfa_method": user.mfa_method,
                    "temp_token": jwt_handler.create_mfa_token(
                        subject=user.username,
                        user_id=user.id,
                    ),
                }

            # Verify MFA code
            if not await mfa_handler.verify_code(
                user=user,
                code=mfa_code,
            ):
                audit_logger.log_login(
                    user_id=user.id,
                    username=username,
                    success=False,
                    ip_address=ip_address,
                    failure_reason="Invalid MFA code",
                )
                raise UnauthorizedException(message="Invalid MFA code")

        # Create tokens
        access_token, refresh_token = await user_service.create_tokens(user)

        # Create session
        session = await user_service.create_session(
            db=db,
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        audit_logger.log_login(
            user_id=user.id,
            username=username,
            success=True,
            ip_address=ip_address,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user,
        }

    async def login_with_mfa(
        self,
        db: AsyncSession,
        temp_token: str,
        mfa_code: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> dict:
        """Complete login after MFA verification."""
        payload = jwt_handler.verify_mfa_token(temp_token)
        user_id = payload.get("user_id")

        user = await user_service.get_user_by_id(db, user_id)

        # Verify MFA code
        if not await mfa_handler.verify_code(user=user, code=mfa_code):
            audit_logger.log_login(
                user_id=user.id,
                username=user.username,
                success=False,
                ip_address=ip_address,
                failure_reason="Invalid MFA code",
            )
            raise UnauthorizedException(message="Invalid MFA code")

        # Create tokens
        access_token, refresh_token = await user_service.create_tokens(user)

        # Create session
        session = await user_service.create_session(
            db=db,
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        audit_logger.log_login(
            user_id=user.id,
            username=user.username,
            success=True,
            ip_address=ip_address,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user,
        }

    async def refresh_token(
        self,
        db: AsyncSession,
        refresh_token: str,
    ) -> dict:
        """Refresh access and refresh tokens."""
        user, access_token, new_refresh_token = await user_service.refresh_tokens(
            db=db,
            refresh_token=refresh_token,
        )

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def logout(
        self,
        db: AsyncSession,
        user_id: int,
        refresh_token: Optional[str] = None,
        all_sessions: bool = False,
    ) -> None:
        """Logout user and invalidate session(s)."""
        await user_service.logout(
            db=db,
            user_id=user_id,
            refresh_token=refresh_token,
            all_sessions=all_sessions,
        )

    async def get_active_sessions(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> List[UserSession]:
        """Get all active sessions for user."""
        result = await db.execute(
            select(UserSession).where(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow(),
                )
            )
        )
        return list(result.scalars().all())

    async def revoke_session(
        self,
        db: AsyncSession,
        user_id: int,
        session_id: int,
    ) -> None:
        """Revoke a specific session."""
        result = await db.execute(
            select(UserSession).where(
                and_(
                    UserSession.id == session_id,
                    UserSession.user_id == user_id,
                )
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise NotFoundException(message="Session not found")

        session.is_active = False
        await db.flush()

    async def enable_mfa(
        self,
        db: AsyncSession,
        user_id: int,
        method: str = "totp",
    ) -> dict:
        """Enable MFA for user."""
        user = await user_service.get_user_by_id(db, user_id)

        if user.mfa_enabled:
            raise ValidationException(message="MFA is already enabled")

        # Generate MFA secret
        secret, qr_code = await mfa_handler.generate_secret(user=user)

        user.mfa_secret = secret
        user.mfa_method = method
        user.mfa_enabled = True

        await db.flush()

        audit_logger.log(
            action=AuditAction.MFA_ENABLED,
            user_id=user_id,
            details={"method": method},
        )

        return {
            "secret": secret,
            "qr_code": qr_code,
        }

    async def verify_mfa_setup(
        self,
        db: AsyncSession,
        user_id: int,
        code: str,
    ) -> bool:
        """Verify MFA setup with a code."""
        user = await user_service.get_user_by_id(db, user_id)

        if not user.mfa_secret:
            raise ValidationException(message="MFA is not set up")

        is_valid = await mfa_handler.verify_code(user=user, code=code)

        if is_valid:
            user.mfa_verified = True
            await db.flush()

            audit_logger.log(
                action=AuditAction.MFA_VERIFIED,
                user_id=user_id,
            )

        return is_valid

    async def disable_mfa(
        self,
        db: AsyncSession,
        user_id: int,
        password: str,
    ) -> None:
        """Disable MFA for user."""
        user = await user_service.get_user_by_id(db, user_id)

        # Verify password first
        if not jwt_handler.verify_password(password, user.password_hash):
            raise UnauthorizedException(message="Invalid password")

        user.mfa_enabled = False
        user.mfa_verified = False
        user.mfa_secret = None
        user.mfa_method = None

        await db.flush()

        audit_logger.log(
            action=AuditAction.MFA_DISABLED,
            user_id=user_id,
        )

    async def change_password(
        self,
        db: AsyncSession,
        user_id: int,
        old_password: str,
        new_password: str,
    ) -> None:
        """Change user password."""
        user = await user_service.get_user_by_id(db, user_id)

        # Verify old password
        if not jwt_handler.verify_password(old_password, user.password_hash):
            audit_logger.log(
                action=AuditAction.PASSWORD_CHANGE_FAILED,
                user_id=user_id,
                details={"reason": "Invalid old password"},
            )
            raise UnauthorizedException(message="Invalid old password")

        # Update password
        user.password_hash = jwt_handler.hash_password(new_password)
        user.password_changed_at = datetime.utcnow()

        # Invalidate all sessions except current
        await self.logout(db=db, user_id=user_id, all_sessions=True)

        await db.flush()

        audit_logger.log(
            action=AuditAction.PASSWORD_CHANGED,
            user_id=user_id,
        )

    async def reset_password(
        self,
        db: AsyncSession,
        user_id: int,
        new_password: str,
        reset_by: Optional[int] = None,
    ) -> None:
        """Reset user password (admin or forgot password flow)."""
        user = await user_service.get_user_by_id(db, user_id)

        user.password_hash = jwt_handler.hash_password(new_password)
        user.password_changed_at = datetime.utcnow()

        # Invalidate all sessions
        await self.logout(db=db, user_id=user_id, all_sessions=True)

        await db.flush()

        audit_logger.log(
            action=AuditAction.PASSWORD_RESET,
            user_id=user_id,
            performed_by=reset_by,
        )


# Singleton instance
auth_service = AuthService()
