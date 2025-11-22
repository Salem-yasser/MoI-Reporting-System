from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db_ops

from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportListResponse,
    ReportStatusUpdate,
    ReportStatus,
    ReportCategory
)
from app.services.report_service import ReportService

router = APIRouter()

@router.post(
    "/",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new report"
)
def create_report(
    report: ReportCreate,
    db: Session = Depends(get_db_ops)
):
    """Submit a new incident report"""
    return ReportService.create_report(db, report)

@router.get(
    "/",
    response_model=ReportListResponse,
    summary="List all reports"
)
def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[ReportStatus] = Query(None),
    category: Optional[ReportCategory] = Query(None),
    db: Session = Depends(get_db_ops)
):
    """Get paginated list of reports"""
    status_value = status.value if status else None
    category_value = category.value if category else None
    
    return ReportService.list_reports(
        db, 
        skip=skip, 
        limit=limit,
        status=status_value,
        category=category_value
    )

@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get report by ID"
)
def get_report(
    report_id: str,
    db: Session = Depends(get_db_ops)
):
    """Get a single report by its ID"""
    report = ReportService.get_report(db, report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    
    return report

@router.put(
    "/{report_id}/status",
    response_model=ReportResponse,
    summary="Update report status"
)
def update_report_status(
    report_id: str,
    status_update: ReportStatusUpdate,
    db: Session = Depends(get_db_ops)
):
    """Update the status of a report"""
    report = ReportService.update_report_status(db, report_id, status_update)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    
    return report

@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a report"
)
def delete_report(
    report_id: str,
    db: Session = Depends(get_db_ops)
):
    """Delete a report permanently"""
    success = ReportService.delete_report(db, report_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    
    return None
