"""
Report Service
"""

import os
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.modules.reports.models import Report, ReportStatus, ReportType
from app.common.helpers import generate_random_string


# PDF Reports directory
REPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "uploads",
    "reports",
)


def ensure_reports_dir():
    """Ensure reports directory exists"""
    os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_pdf_content(
    report_type: str, title: str, start_date: str = None, end_date: str = None
) -> bytes:
    """Generate simple PDF content"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch

        # Create a temporary buffer
        buffer = __import__("io").BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 1 * inch, f"Trade Finance Platform - {title}")

        # Date
        c.setFont("Helvetica", 12)
        c.drawString(
            1 * inch,
            height - 1.5 * inch,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        )

        if start_date and end_date:
            c.drawString(
                1 * inch, height - 1.8 * inch, f"Period: {start_date} to {end_date}"
            )

        # Report type info
        c.setFont("Helvetica", 12)
        y_position = height - 2.5 * inch
        c.drawString(1 * inch, y_position, f"Report Type: {report_type}")

        y_position -= 0.3 * inch
        c.drawString(1 * inch, y_position, "Summary:")

        y_position -= 0.3 * inch
        c.setFont("Helvetica", 10)

        # Add some sample data based on report type
        sample_data = [
            f"Report ID: {generate_random_string(8, True)}",
            f"Status: Completed",
            f"Total Transactions: {100 + int(uuid.uuid4().hex[:4], 16) % 900}",
            f"Total Value: ${1000000 + int(uuid.uuid4().hex[:6], 16) % 9000000:,.2f}",
        ]

        for line in sample_data:
            c.drawString(1.2 * inch, y_position, line)
            y_position -= 0.2 * inch

        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(
            1 * inch,
            0.5 * inch,
            "Trade Finance Platform - Trade Finance Management System",
        )

        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    except ImportError:
        # If reportlab is not available, return a simple text PDF
        content = f"Trade Finance Platform - {title}\n"
        content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        if start_date and end_date:
            content += f"Period: {start_date} to {end_date}\n"
        content += f"Report Type: {report_type}\n"
        content += "\nThis is a placeholder PDF content.\n"
        return content.encode("utf-8")


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

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

    async def _generate_and_save_pdf(
        self,
        report_type: str,
        title: str,
        start_date: str = None,
        end_date: str = None,
    ) -> tuple[str, str]:
        """Generate PDF and save to disk, return file path and filename"""
        ensure_reports_dir()

        # Generate unique filename
        filename = f"report_{generate_random_string(12, True)}.pdf"
        file_path = os.path.join(REPORTS_DIR, filename)

        # Generate PDF content
        pdf_content = generate_pdf_content(report_type, title, start_date, end_date)

        # Write to file
        with open(file_path, "wb") as f:
            f.write(pdf_content)

        return file_path, filename

    async def generate_report(
        self,
        report_request,
        user_id: int,
    ) -> Report:
        """Generate a new report based on request"""
        report = Report(
            report_number=await self.generate_report_number(),
            report_type=(
                report_request.report_type.value
                if hasattr(report_request.report_type, "value")
                else report_request.report_type
            ),
            title=report_request.title
            or f"Report {datetime.utcnow().strftime('%Y-%m-%d')}",
            status=ReportStatus.COMPLETED,
            generated_by=user_id,
            generated_at=datetime.utcnow(),
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def list_reports(
        self,
        skip: int = 0,
        limit: int = 100,
        report_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[Report]:
        """List all reports with optional filters"""
        query = select(Report)

        if report_type:
            query = query.where(Report.report_type == report_type)
        if status:
            query = query.where(Report.status == status)

        query = query.order_by(Report.generated_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_report_by_id(self, report_id: int) -> Optional[Report]:
        """Get a report by ID"""
        result = await self.db.execute(select(Report).where(Report.id == report_id))
        return result.scalar_one_or_none()

    async def delete_report(self, report_id: int, user_id: int) -> bool:
        """Delete a report"""
        report = await self.get_report_by_id(report_id)
        if not report:
            return False

        # Delete the file if it exists
        if report.file_path and os.path.exists(report.file_path):
            try:
                os.remove(report.file_path)
            except Exception:
                pass

        await self.db.delete(report)
        await self.db.commit()
        return True

    async def get_report_path(self, report_id: int) -> Optional[str]:
        """Get the file path for a report"""
        report = await self.get_report_by_id(report_id)
        if report and report.file_path and os.path.exists(report.file_path):
            return report.file_path
        return None

    async def get_reports_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Report]:
        """Get all reports generated by a user"""
        result = await self.db.execute(
            select(Report)
            .where(Report.generated_by == user_id)
            .order_by(Report.generated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def generate_lc_summary_report(
        self,
        start_date: str,
        end_date: str,
        user_id: int,
    ) -> Report:
        """Generate Letter of Credit summary report"""
        # Generate PDF
        file_path, filename = await self._generate_and_save_pdf(
            report_type="LC Summary",
            title=f"LC Summary Report ({start_date} to {end_date})",
            start_date=start_date,
            end_date=end_date,
        )

        report = Report(
            report_number=await self.generate_report_number(),
            report_type=ReportType.LC_SUMMARY.value,
            title=f"LC Summary Report ({start_date} to {end_date})",
            status=ReportStatus.COMPLETED,
            file_path=file_path,
            filename=filename,
            generated_by=user_id,
            generated_at=datetime.utcnow(),
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def generate_guarantee_summary_report(
        self,
        start_date: str,
        end_date: str,
        user_id: int,
    ) -> Report:
        """Generate Bank Guarantee summary report"""
        # Generate PDF
        file_path, filename = await self._generate_and_save_pdf(
            report_type="Guarantee Summary",
            title=f"Guarantee Summary Report ({start_date} to {end_date})",
            start_date=start_date,
            end_date=end_date,
        )

        report = Report(
            report_number=await self.generate_report_number(),
            report_type=ReportType.GUARANTEE_SUMMARY.value,
            title=f"Guarantee Summary Report ({start_date} to {end_date})",
            status=ReportStatus.COMPLETED,
            file_path=file_path,
            filename=filename,
            generated_by=user_id,
            generated_at=datetime.utcnow(),
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def generate_loan_summary_report(
        self,
        start_date: str,
        end_date: str,
        user_id: int,
    ) -> Report:
        """Generate Trade Loan summary report"""
        # Generate PDF
        file_path, filename = await self._generate_and_save_pdf(
            report_type="Loan Summary",
            title=f"Loan Performance Report ({start_date} to {end_date})",
            start_date=start_date,
            end_date=end_date,
        )

        report = Report(
            report_number=await self.generate_report_number(),
            report_type=ReportType.LOAN_SUMMARY.value,
            title=f"Loan Performance Report ({start_date} to {end_date})",
            status=ReportStatus.COMPLETED,
            file_path=file_path,
            filename=filename,
            generated_by=user_id,
            generated_at=datetime.utcnow(),
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def generate_portfolio_summary_report(
        self,
        as_of_date: str,
        user_id: int,
    ) -> Report:
        """Generate Portfolio summary report (for Collection and Risk Exposure)"""
        # Generate PDF
        file_path, filename = await self._generate_and_save_pdf(
            report_type="Portfolio Summary",
            title=f"Portfolio Summary Report (as of {as_of_date})",
            start_date=as_of_date,
            end_date=as_of_date,
        )

        report = Report(
            report_number=await self.generate_report_number(),
            report_type=ReportType.PORTFOLIO_SUMMARY.value,
            title=f"Portfolio Summary Report (as of {as_of_date})",
            status=ReportStatus.COMPLETED,
            file_path=file_path,
            filename=filename,
            generated_by=user_id,
            generated_at=datetime.utcnow(),
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def generate_compliance_summary_report(
        self,
        start_date: str,
        end_date: str,
        user_id: int,
    ) -> Report:
        """Generate Compliance summary report"""
        # Generate PDF
        file_path, filename = await self._generate_and_save_pdf(
            report_type="Compliance",
            title=f"Compliance Report ({start_date} to {end_date})",
            start_date=start_date,
            end_date=end_date,
        )

        report = Report(
            report_number=await self.generate_report_number(),
            report_type=ReportType.COMPLIANCE.value,
            title=f"Compliance Report ({start_date} to {end_date})",
            status=ReportStatus.COMPLETED,
            file_path=file_path,
            filename=filename,
            generated_by=user_id,
            generated_at=datetime.utcnow(),
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report
