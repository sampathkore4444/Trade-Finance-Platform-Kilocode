"""
Notifications Router
Handles HTTP endpoints for notification management
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from fastapi.security import HTTPBearer

from app.database import get_db
from app.core.auth.jwt_handler import get_current_user
from app.modules.notifications.schemas import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationStatus,
    NotificationType,
)
from app.modules.notifications.services import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])
security = HTTPBearer()


def get_notification_service(db=Depends(get_db)):
    """Dependency to get notification service"""
    return NotificationService(db)


@router.post(
    "/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED
)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Create a new notification
    """
    notification = await service.create_notification(
        notification_data=notification_data,
        user_id=current_user["user_id"],
    )
    return notification


@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[NotificationStatus] = None,
    notification_type: Optional[NotificationType] = None,
    is_read: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """
    List all notifications with optional filters
    """
    notifications = await service.list_notifications(
        user_id=current_user["user_id"],
        skip=skip,
        limit=limit,
        status=status,
        notification_type=notification_type,
        is_read=is_read,
    )
    return notifications


@router.get("/unread/count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Get count of unread notifications
    """
    count = await service.get_unread_count(
        user_id=current_user["user_id"],
    )
    return {"unread_count": count}


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Get a notification by ID
    """
    notification = await service.get_notification_by_id(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return notification


@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: UUID,
    notification_data: NotificationUpdate,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Update a notification
    """
    notification = await service.update_notification(
        notification_id=notification_id,
        notification_data=notification_data,
        user_id=current_user["user_id"],
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return notification


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Mark notification as read
    """
    notification = await service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user["user_id"],
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return notification


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_as_read(
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Mark all notifications as read
    """
    await service.mark_all_as_read(
        user_id=current_user["user_id"],
    )


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Delete a notification
    """
    success = await service.delete_notification(
        notification_id=notification_id,
        user_id=current_user["user_id"],
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )


@router.delete("/clear-all", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_notifications(
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Clear all notifications for the current user
    """
    await service.clear_all_notifications(
        user_id=current_user["user_id"],
    )


@router.post("/send", response_model=List[NotificationResponse])
async def send_notifications(
    user_ids: List[UUID],
    notification_data: NotificationCreate,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Send notifications to multiple users (admin function)
    """
    notifications = await service.send_bulk_notifications(
        user_ids=user_ids,
        notification_data=notification_data,
        sender_id=current_user["user_id"],
    )
    return notifications


@router.post("/broadcast", response_model=List[NotificationResponse])
async def broadcast_notification(
    notification_data: NotificationCreate,
    role_ids: Optional[List[UUID]] = None,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Broadcast notification to all users or specific roles (admin function)
    """
    notifications = await service.broadcast_notification(
        notification_data=notification_data,
        role_ids=role_ids,
        sender_id=current_user["user_id"],
    )
    return notifications
