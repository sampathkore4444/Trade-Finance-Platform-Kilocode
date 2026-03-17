"""
Report Service
"""

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reports.models import Report
from app.common.helpers import generate_random_string


class ReportService:
    async def generate_report_number(self) -> str:
        return f"RPT{generate_random_string(8, True)}"

    async def create_report(
        self,
        db: AsyncSession,
        report_type: str,
        title: str,
        generated_by: int,
        **kwargs,
    ) -> Report:
        report = Report(
            report_number=await self.generate_report_number(),
            report_type=report_type,
            title=title,
            generated_by=generated_by,
            generated_at=datetime.utcnow(),
            **kwargs,
        )
        db.add(report)
        await db.flush()
        return report


report_service = ReportService()
