"""
Notifications Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum


class NotificationTypeEnum(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationBase(BaseModel):
    notification_type: NotificationTypeEnum
    title: Optional[str] = None
    message: Optional[str] = None


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
