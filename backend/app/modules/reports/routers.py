"""
Reports Router
Handles HTTP endpoints for report generation and management
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer

from app.database import get_db
from app.core.auth.jwt_handler import get_current_user
from app.modules.reports.schemas import (
    ReportGenerationRequest,
    ReportResponse,
    ReportStatus,
    ReportType,
)
from app.modules.reports.services import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])
security = HTTPBearer()


def get_report_service(db=Depends(get_db)):
    """Dependency to get report service"""
    return ReportService(db)


@router.post(
    "/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED
)
async def generate_report(
    report_request: ReportGenerationRequest,
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """
    Generate a new report
    """
    report = await service.generate_report(
        report_request=report_request,
        user_id=current_user["user_id"],
    )
    return report


@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    report_type: Optional[ReportType] = None,
    status: Optional[ReportStatus] = None,
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """
    List all reports with optional filters
    """
    reports = await service.list_reports(
        skip=skip,
        limit=limit,
        report_type=report_type,
        status=status,
    )
    return reports


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """
    Get a report by ID
    """
    report = await service.get_report_by_id(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return report


@router.get("/{report_id}/download")
async def download_report(
    report_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """
    Download a generated report
    """
    report = await service.get_report_by_id(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    if report.status != ReportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report is not ready for download",
        )

    file_path = await service.get_report_path(report_id)
    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found",
        )

    return FileResponse(
        path=file_path,
        filename=report.filename,
        media_type="application/pdf",
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """
    Delete a report
    """
    success = await service.delete_report(
        report_id=report_id,
        user_id=current_user["user_id"],
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )


@router.get("/lc/summary", response_model=ReportResponse)
async def get_lc_summary_report(
    start_date: str,
    end_date: str,
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """
    Generate Letter of Credit summary report
    """
    report = await service.generate_lc_summary_report(
        start_date=start_date,
        end_date=end_date,
        user_id=current_user["user_id"],
    )
    return report


@router.get("/guarantee/summary", response_model=ReportResponse)
async def get_guarantee_summary_report(
    start_date: str,
    end_date: str,
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """
    Generate Bank Guarantee summary report
    """
    report = await service.generate_guarantee_summary_report(
        start_date=start_date,
        end_date=end_date,
        user_id=current_user["user_id"],
    )
    return report


@router.get("/loan/summary", response_model=ReportResponse)
async def get_loan_summary_report(
    start_date: str,
    end_date: str,
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """
    Generate Trade Loan summary report
    """
    report = await service.generate_loan_summary_report(
        start_date=start_date,
        end_date=end_date,
        user_id=current_user["user_id"],
    )
    return report


@router.get("/portfolio/summary", response_model=ReportResponse)
async def get_portfolio_summary_report(
    as_of_date: str,
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """
    Generate Portfolio summary report
    """
    report = await service.generate_portfolio_summary_report(
        as_of_date=as_of_date,
        user_id=current_user["user_id"],
    )
    return report


@router.get("/compliance/summary", response_model=ReportResponse)
async def get_compliance_summary_report(
    start_date: str,
    end_date: str,
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """
    Generate Compliance summary report
    """
    report = await service.generate_compliance_summary_report(
        start_date=start_date,
        end_date=end_date,
        user_id=current_user["user_id"],
    )
    return report


@router.get("/user/{user_id}", response_model=List[ReportResponse])
async def get_reports_by_user(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
):
    """
    Get all reports generated by a user
    """
    reports = await service.get_reports_by_user(
        user_id=user_id,
        skip=skip,
        limit=limit,
    )
    return reports
