"""
Risk Management Service
"""

from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.risk_management.models import RiskAssessment, RiskLevel
from app.common.exceptions import NotFoundException


class RiskManagementService:
    async def create_assessment(
        self,
        db: AsyncSession,
        entity_type: str,
        entity_id: int,
        risk_type: str,
        risk_level: RiskLevel,
        score: Optional[float],
        assessed_by: int,
        **kwargs,
    ) -> RiskAssessment:
        assessment = RiskAssessment(
            entity_type=entity_type,
            entity_id=entity_id,
            risk_type=risk_type,
            risk_level=risk_level,
            score=score,
            assessed_by=assessed_by,
            assessment_date=datetime.utcnow(),
            **kwargs,
        )
        db.add(assessment)
        await db.flush()
        return assessment

    async def get_assessment_by_id(
        self, db: AsyncSession, assessment_id: int
    ) -> RiskAssessment:
        result = await db.execute(
            select(RiskAssessment).where(RiskAssessment.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()
        if not assessment:
            raise NotFoundException(f"Assessment {assessment_id} not found")
        return assessment

    async def list_assessments(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        entity_type: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None,
    ) -> Tuple[List[RiskAssessment], int]:
        query = select(RiskAssessment)
        filters = []
        if entity_type:
            filters.append(RiskAssessment.entity_type == entity_type)
        if risk_level:
            filters.append(RiskAssessment.risk_level == risk_level)
        if filters:
            query = query.where(and_(*filters))
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query) or 0
        query = (
            query.offset((page - 1) * page_size)
            .limit(page_size)
            .order_by(RiskAssessment.assessment_date.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all()), total


risk_service = RiskManagementService()
