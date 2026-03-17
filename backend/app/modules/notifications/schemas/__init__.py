"""
Notifications Schemas Package
"""

from app.modules.notifications.schemas.notification import (
    NotificationBase,
    NotificationResponse,
    NotificationTypeEnum,
)

# Aliases for backward compatibility
NotificationCreate = NotificationBase
NotificationUpdate = NotificationBase
NotificationStatus = NotificationTypeEnum
NotificationType = NotificationTypeEnum

__all__ = [
    "NotificationBase",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    "NotificationTypeEnum",
    "NotificationStatus",
    "NotificationType",
]
