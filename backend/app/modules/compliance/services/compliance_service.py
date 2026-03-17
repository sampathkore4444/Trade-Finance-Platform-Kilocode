"""
Compliance Service
"""

from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.compliance.models import ComplianceCheck, ComplianceStatus
from app.common.exceptions import NotFoundException


class ComplianceService:
    async def create_check(
        self,
        db: AsyncSession,
        entity_type: str,
        entity_id: int,
        check_type: str,
        checked_by: int,
        **kwargs,
    ) -> ComplianceCheck:
        check = ComplianceCheck(
            entity_type=entity_type,
            entity_id=entity_id,
            check_type=check_type,
            checked_by=checked_by,
            **kwargs,
        )
        db.add(check)
        await db.flush()
        return check

    async def get_check_by_id(self, db: AsyncSession, check_id: int) -> ComplianceCheck:
        result = await db.execute(
            select(ComplianceCheck).where(ComplianceCheck.id == check_id)
        )
        check = result.scalar_one_or_none()
        if not check:
            raise NotFoundException(f"Check {check_id} not found")
        return check


compliance_service = ComplianceService()
