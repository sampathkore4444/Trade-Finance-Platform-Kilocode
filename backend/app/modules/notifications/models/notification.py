"""
Notifications Model
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    Boolean,
)
from sqlalchemy.sql import func
from app.database import Base
import enum


class NotificationType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    notification_type = Column(Enum(NotificationType), default=NotificationType.IN_APP)
    title = Column(String(255))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    read_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
