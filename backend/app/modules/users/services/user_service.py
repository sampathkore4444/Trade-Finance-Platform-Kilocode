"""
User Service for Trade Finance Platform

This module contains business logic for user operations.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.users.models.user import User, UserStatus
from app.modules.users.models.role import Role
from app.modules.users.models.session import UserSession
from app.core.auth.jwt_handler import jwt_handler
from app.core.security.audit_logger import audit_logger, AuditAction
from app.common.exceptions import (
    NotFoundException,
    DuplicateResourceException,
    UnauthorizedException,
)
from app.common.validators import validate_email, validate_password
from app.config import settings


class UserService:
    """Service for user-related operations."""

    async def create_user(
        self,
        db: AsyncSession,
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        organization_id: Optional[int] = None,
        branch_id: Optional[int] = None,
        department_id: Optional[int] = None,
        role_ids: Optional[List[int]] = None,
        created_by: Optional[int] = None,
    ) -> User:
        """Create a new user."""
        validate_email(email)
        validate_password(password)

        # Check for duplicate username
        result = await db.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            raise DuplicateResourceException(
                message=f"Username '{username}' already exists"
            )

        # Check for duplicate email
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise DuplicateResourceException(message=f"Email '{email}' already exists")

        # Hash password
        password_hash = jwt_handler.hash_password(password)

        # Create full name
        full_name = f"{first_name or ''} {last_name or ''}".strip()

        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            phone=phone,
            organization_id=organization_id,
            branch_id=branch_id,
            department_id=department_id,
            status=UserStatus.ACTIVE if not created_by else UserStatus.PENDING,
            created_by=created_by,
        )

        # Assign roles
        if role_ids:
            result = await db.execute(select(Role).where(Role.id.in_(role_ids)))
            roles = result.scalars().all()
            user.roles = list(roles)

        db.add(user)
        await db.flush()

        audit_logger.log(
            action=AuditAction.USER_CREATED,
            user_id=created_by,
            resource_type="USER",
            resource_id=str(user.id),
            details={"username": username, "email": email},
        )

        return user

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> User:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException(message=f"User with ID {user_id} not found")

        return user

    # Alias for backward compatibility
    async def get_by_id(self, db: AsyncSession, user_id: int) -> User:
        """Get user by ID (alias for get_user_by_id)."""
        return await self.get_user_by_id(db, user_id)

    async def get_user_by_username(
        self, db: AsyncSession, username: str
    ) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(
            select(User)
            .where(User.username == username)
            .options(selectinload(User.roles))
        )
        return result.scalar_one_or_none()

    async def authenticate_user(
        self,
        db: AsyncSession,
        username: str,
        password: str,
        ip_address: Optional[str] = None,
    ) -> User:
        """Authenticate a user."""
        user = await self.get_user_by_username(db, username)

        if not user:
            audit_logger.log_login(
                user_id=0,
                username=username,
                success=False,
                ip_address=ip_address,
                failure_reason="User not found",
            )
            raise UnauthorizedException(message="Invalid username or password")

        # Check if user is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise UnauthorizedException(message="Account is locked")

        # Verify password
        if not jwt_handler.verify_password(password, user.password_hash):
            user.failed_login_attempts += 1

            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=settings.ACCOUNT_LOCKOUT_MINUTES
                )
                user.status = UserStatus.LOCKED

            await db.flush()
            raise UnauthorizedException(message="Invalid username or password")

        # Reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.utcnow()
        user.last_login_ip = ip_address

        await db.flush()

        return user

    async def create_tokens(self, user: User) -> Tuple[str, str]:
        """Create access and refresh tokens for user."""
        # Use empty lists to avoid lazy loading issues in async context
        roles = []
        permissions = []

        access_token = jwt_handler.create_access_token(
            subject=user.username,
            user_id=user.id,
            roles=roles,
            permissions=permissions,
        )

        refresh_token = jwt_handler.create_refresh_token(
            subject=user.username,
            user_id=user.id,
        )

        return access_token, refresh_token

    async def create_session(
        self,
        db: AsyncSession,
        user_id: int,
        access_token: str,
        refresh_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSession:
        """Create user session."""
        expires_at = jwt_handler.get_token_expiry(access_token)

        session = UserSession(
            user_id=user_id,
            token=access_token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        db.add(session)
        await db.flush()

        return session

    async def refresh_tokens(
        self,
        db: AsyncSession,
        refresh_token: str,
    ) -> Tuple[User, str, str]:
        """Refresh access and refresh tokens."""
        payload = jwt_handler.verify_refresh_token(refresh_token)
        user_id = payload.get("user_id")

        user = await self.get_user_by_id(db, user_id)

        # Verify session
        result = await db.execute(
            select(UserSession).where(
                and_(
                    UserSession.refresh_token == refresh_token,
                    UserSession.is_active == True,
                )
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise UnauthorizedException(message="Invalid session")

        access_token, new_refresh_token = await self.create_tokens(user)

        session.token = access_token
        session.refresh_token = new_refresh_token
        session.expires_at = jwt_handler.get_token_expiry(access_token)

        await db.flush()

        return user, access_token, new_refresh_token

    async def logout(
        self,
        db: AsyncSession,
        user_id: int,
        refresh_token: Optional[str] = None,
        all_sessions: bool = False,
    ) -> None:
        """Logout user."""
        if all_sessions:
            result = await db.execute(
                select(UserSession).where(
                    and_(
                        UserSession.user_id == user_id,
                        UserSession.is_active == True,
                    )
                )
            )
            sessions = result.scalars().all()
            for session in sessions:
                session.is_active = False
        else:
            result = await db.execute(
                select(UserSession).where(
                    and_(
                        UserSession.refresh_token == refresh_token,
                        UserSession.user_id == user_id,
                    )
                )
            )
            session = result.scalar_one_or_none()
            if session:
                session.is_active = False

        await db.flush()

        audit_logger.log(
            action=AuditAction.LOGOUT,
            user_id=user_id,
        )

    async def list_users(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status: Optional[UserStatus] = None,
        organization_id: Optional[int] = None,
    ) -> Tuple[List[User], int]:
        """List users with pagination."""
        query = select(User)

        filters = []
        if search:
            filters.append(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%"),
                )
            )
        if status:
            filters.append(User.status == status)
        if organization_id:
            filters.append(User.organization_id == organization_id)

        if filters:
            query = query.where(and_(*filters))

        from sqlalchemy import func

        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0

        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        users = result.scalars().all()

        return list(users), total

    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        **kwargs,
    ) -> User:
        """Update user."""
        user = await self.get_user_by_id(db, user_id)

        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        if "first_name" in kwargs or "last_name" in kwargs:
            user.full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

        await db.flush()

        return user

    async def delete_user(self, db: AsyncSession, user_id: int) -> None:
        """Delete user."""
        user = await self.get_user_by_id(db, user_id)
        await db.delete(user)
        await db.flush()

    async def assign_roles(
        self,
        db: AsyncSession,
        user_id: int,
        role_ids: List[int],
    ) -> User:
        """Assign roles to user."""
        user = await self.get_user_by_id(db, user_id)

        result = await db.execute(select(Role).where(Role.id.in_(role_ids)))
        roles = result.scalars().all()

        user.roles = list(roles)

        await db.flush()

        return user


# Singleton instance
user_service = UserService()


# Module-level function for backward compatibility
async def get_by_id(db: AsyncSession, user_id: int) -> User:
    """Get user by ID - module-level function for backward compatibility."""
    return await user_service.get_by_id(db, user_id)
