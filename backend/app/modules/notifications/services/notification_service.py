"""
Notification Service
"""

from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification
from app.common.exceptions import NotFoundException


class NotificationService:
    async def create_notification(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        **kwargs
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            sent_at=datetime.utcnow(),
            **kwargs,
        )
        db.add(notification)
        await db.flush()
        return notification

    async def get_user_notifications(
        self, db: AsyncSession, user_id: int, page: int = 1, page_size: int = 20
    ) -> Tuple[List[Notification], int]:
        query = select(Notification).where(Notification.user_id == user_id)
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        query = (
            query.offset((page - 1) * page_size)
            .limit(page_size)
            .order_by(Notification.created_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all()), total


notification_service = NotificationService()
