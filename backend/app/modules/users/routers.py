"""
User Routers for Trade Finance Platform

This module defines API routes for user operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.modules.users.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserProfileResponse,
    UserRolesUpdate,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
)
from app.modules.users.services import user_service, auth_service
from app.core.auth.jwt_handler import jwt_handler
from app.core.auth.rbac_handler import rbac_handler, Permission
from app.common.exceptions import UnauthorizedException, ValidationException


router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get current authenticated user.
    """
    try:
        token = credentials.credentials
        payload = jwt_handler.verify_access_token(token)

        user_id = payload.get("user_id")
        user = await user_service.get_user_by_id(db, user_id)

        # Return user data for authorization
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": [role.name for role in user.roles],
            "permissions": user.permissions,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return tokens.
    """
    try:
        result = await auth_service.login(
            db=db,
            username=request.username,
            password=request.password,
            ip_address=None,  # Could be passed from request context
        )

        await db.commit()

        user = result["user"]

        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"],
            user=UserProfileResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                organization_id=user.organization_id,
                branch_id=user.branch_id,
                department_id=user.department_id,
                mfa_enabled=user.mfa_enabled,
                last_login_at=user.last_login_at,
                created_at=user.created_at,
                roles=[r.name for r in user.roles],
                permissions=user.permissions,
            ),
        )
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token.
    """
    try:
        result = await auth_service.refresh_token(
            db=db,
            refresh_token=request.refresh_token,
        )

        await db.commit()

        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"],
            user=None,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )


@router.post("/logout")
async def logout(
    request: LogoutRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user.
    """
    await auth_service.logout(
        db=db,
        user_id=current_user["user_id"],
        refresh_token=request.refresh_token,
        all_sessions=request.all_sessions,
    )

    await db.commit()

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user profile.
    """
    user = await user_service.get_user_by_id(db, current_user["user_id"])

    return UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        organization_id=user.organization_id,
        branch_id=user.branch_id,
        department_id=user.department_id,
        mfa_enabled=user.mfa_enabled,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        roles=[r.name for r in user.roles],
        permissions=current_user["permissions"],
    )


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    organization_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List users with pagination.
    """
    # Check permission
    if not rbac_handler.has_permission(current_user["roles"], Permission.USER_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    users, total = await user_service.list_users(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        organization_id=organization_id,
    )

    total_pages = (total + page_size - 1) // page_size

    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.USER_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    try:
        user = await user_service.create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            organization_id=user_data.organization_id,
            branch_id=user_data.branch_id,
            department_id=user_data.department_id,
            role_ids=user_data.role_ids,
            created_by=current_user["user_id"],
        )

        await db.commit()

        return UserResponse.model_validate(user)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user by ID.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.USER_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    user = await user_service.get_user_by_id(db, user_id)

    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.USER_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    user = await user_service.update_user(
        db=db,
        user_id=user_id,
        **user_data.model_dump(exclude_unset=True),
    )

    await db.commit()

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.USER_DELETE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    await user_service.delete_user(db, user_id)

    await db.commit()


@router.post("/{user_id}/roles", response_model=UserResponse)
async def update_user_roles(
    user_id: int,
    data: UserRolesUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user roles.
    """
    if not rbac_handler.has_permission(current_user["roles"], Permission.USER_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    user = await user_service.assign_roles(
        db=db,
        user_id=user_id,
        role_ids=data.role_ids,
    )

    await db.commit()

    return UserResponse.model_validate(user)


@router.post("/mfa/setup")
async def setup_mfa(
    method: str = "totp",
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Setup MFA for current user.
    """
    mfa_data = await auth_service.enable_mfa(
        db=db,
        user_id=current_user["user_id"],
        method=method,
    )

    await db.commit()

    return mfa_data


@router.post("/mfa/verify")
async def verify_mfa(
    code: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify MFA setup with a code.
    """
    is_valid = await auth_service.verify_mfa_setup(
        db=db,
        user_id=current_user["user_id"],
        code=code,
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code",
        )

    await db.commit()

    return {"message": "MFA verified successfully"}


@router.post("/mfa/disable")
async def disable_mfa(
    password: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disable MFA for current user.
    """
    try:
        await auth_service.disable_mfa(
            db=db,
            user_id=current_user["user_id"],
            password=password,
        )

        await db.commit()

        return {"message": "MFA disabled successfully"}
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/sessions")
async def get_sessions(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all active sessions for current user.
    """
    sessions = await auth_service.get_active_sessions(
        db=db,
        user_id=current_user["user_id"],
    )

    return {
        "items": [
            {
                "id": s.id,
                "ip_address": s.ip_address,
                "user_agent": s.user_agent,
                "created_at": s.created_at,
                "expires_at": s.expires_at,
            }
            for s in sessions
        ]
    }


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke a specific session.
    """
    try:
        await auth_service.revoke_session(
            db=db,
            user_id=current_user["user_id"],
            session_id=session_id,
        )

        await db.commit()

        return {"message": "Session revoked successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
