"""
Reports endpoints for generating and managing analytics reports.
"""

from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from app.models.user import User
from app.models.report import Report, ReportCreate, ReportUpdate, ReportResponse, ReportSummary, ReportType, ReportStatus
from app.api.v1.endpoints.auth import get_current_user
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=List[ReportResponse], summary="Get user reports")
async def get_reports(
    current_user: User = Depends(get_current_user),
    status_filter: Optional[ReportStatus] = Query(None, description="Filter by status"),
    report_type: Optional[ReportType] = Query(None, description="Filter by report type"),
    limit: int = Query(50, le=100, description="Number of reports to return"),
    skip: int = Query(0, description="Number of reports to skip")
) -> List[ReportResponse]:
    """Get all reports for the current user."""
    
    query = Report.find(Report.user_id == str(current_user.id))
    
    if status_filter:
        query = query.find(Report.status == status_filter)
    
    if report_type:
        query = query.find(Report.report_type == report_type)
    
    reports = await query.sort(-Report.created_at).skip(skip).limit(limit).to_list()
    
    return [
        ReportResponse(
            id=str(report.id),
            title=report.title,
            description=report.description,
            report_type=report.report_type,
            page_ids=report.page_ids,
            date_from=report.date_from,
            date_to=report.date_to,
            format=report.format,
            status=report.status,
            progress=report.progress,
            file_url=str(report.file_url) if report.file_url else None,
            file_size=report.file_size,
            download_count=report.download_count,
            error_message=report.error_message,
            is_scheduled=report.is_scheduled,
            frequency=report.frequency,
            next_generation=report.next_generation,
            last_generated=report.last_generated,
            created_at=report.created_at,
            updated_at=report.updated_at,
            expires_at=report.expires_at
        )
        for report in reports
    ]


@router.post("/", response_model=ReportResponse, summary="Create new report")
async def create_report(
    report_data: ReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> ReportResponse:
    """Create and generate a new report."""
    
    # Create report record
    report = Report(
        user_id=str(current_user.id),
        title=report_data.title,
        description=report_data.description,
        report_type=report_data.report_type,
        page_ids=report_data.page_ids,
        date_from=report_data.date_from,
        date_to=report_data.date_to,
        format=report_data.format,
        filters=report_data.filters or {},
        parameters=report_data.parameters or {},
        include_charts=report_data.include_charts,
        include_raw_data=report_data.include_raw_data,
        email_recipients=report_data.email_recipients or [],
        is_scheduled=report_data.is_scheduled,
        frequency=report_data.frequency
    )
    
    await report.save()
    
    # Schedule report generation
    background_tasks.add_task(generate_report_task, str(report.id))
    
    # Update user's reports count
    current_user.increment_reports_generated()
    await current_user.save()
    
    logger.info(f"Report created: {report.title} for user {current_user.email}")
    
    return ReportResponse(
        id=str(report.id),
        title=report.title,
        description=report.description,
        report_type=report.report_type,
        page_ids=report.page_ids,
        date_from=report.date_from,
        date_to=report.date_to,
        format=report.format,
        status=report.status,
        progress=report.progress,
        file_url=str(report.file_url) if report.file_url else None,
        file_size=report.file_size,
        download_count=report.download_count,
        error_message=report.error_message,
        is_scheduled=report.is_scheduled,
        frequency=report.frequency,
        next_generation=report.next_generation,
        last_generated=report.last_generated,
        created_at=report.created_at,
        updated_at=report.updated_at,
        expires_at=report.expires_at
    )


@router.get("/{report_id}", response_model=ReportResponse, summary="Get report details")
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
) -> ReportResponse:
    """Get details of a specific report."""
    
    report = await Report.find_one(
        Report.id == report_id,
        Report.user_id == str(current_user.id)
    )
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return ReportResponse(
        id=str(report.id),
        title=report.title,
        description=report.description,
        report_type=report.report_type,
        page_ids=report.page_ids,
        date_from=report.date_from,
        date_to=report.date_to,
        format=report.format,
        status=report.status,
        progress=report.progress,
        file_url=str(report.file_url) if report.file_url else None,
        file_size=report.file_size,
        download_count=report.download_count,
        error_message=report.error_message,
        is_scheduled=report.is_scheduled,
        frequency=report.frequency,
        next_generation=report.next_generation,
        last_generated=report.last_generated,
        created_at=report.created_at,
        updated_at=report.updated_at,
        expires_at=report.expires_at
    )


@router.put("/{report_id}", response_model=ReportResponse, summary="Update report")
async def update_report(
    report_id: str,
    report_update: ReportUpdate,
    current_user: User = Depends(get_current_user)
) -> ReportResponse:
    """Update report settings."""
    
    report = await Report.find_one(
        Report.id == report_id,
        Report.user_id == str(current_user.id)
    )
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Update fields that are provided
    update_data = report_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(report, field, value)
    
    await report.save()
    logger.info(f"Report updated: {report.title}")
    
    return ReportResponse(
        id=str(report.id),
        title=report.title,
        description=report.description,
        report_type=report.report_type,
        page_ids=report.page_ids,
        date_from=report.date_from,
        date_to=report.date_to,
        format=report.format,
        status=report.status,
        progress=report.progress,
        file_url=str(report.file_url) if report.file_url else None,
        file_size=report.file_size,
        download_count=report.download_count,
        error_message=report.error_message,
        is_scheduled=report.is_scheduled,
        frequency=report.frequency,
        next_generation=report.next_generation,
        last_generated=report.last_generated,
        created_at=report.created_at,
        updated_at=report.updated_at,
        expires_at=report.expires_at
    )


@router.delete("/{report_id}", summary="Delete report")
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a report."""
    
    report = await Report.find_one(
        Report.id == report_id,
        Report.user_id == str(current_user.id)
    )
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    await report.delete()
    logger.info(f"Report deleted: {report.title} for user {current_user.email}")
    
    return {"message": "Report successfully deleted"}


@router.post("/{report_id}/download", summary="Download report")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """Download a completed report."""
    
    report = await Report.find_one(
        Report.id == report_id,
        Report.user_id == str(current_user.id)
    )
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if not report.can_be_downloaded():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report is not available for download"
        )
    
    # Increment download count
    report.increment_download_count()
    await report.save()
    
    # In a real implementation, you would return the file or redirect to download URL
    return {
        "download_url": str(report.file_url),
        "file_size": report.file_size,
        "format": report.format
    }


@router.get("/summary/dashboard", response_model=ReportSummary, summary="Get reports summary")
async def get_reports_summary(
    current_user: User = Depends(get_current_user)
) -> ReportSummary:
    """Get reports summary for dashboard."""
    
    # Get counts by status
    total_reports = await Report.find(Report.user_id == str(current_user.id)).count()
    pending_reports = await Report.find(
        Report.user_id == str(current_user.id),
        Report.status == ReportStatus.PENDING
    ).count()
    completed_reports = await Report.find(
        Report.user_id == str(current_user.id),
        Report.status == ReportStatus.COMPLETED
    ).count()
    failed_reports = await Report.find(
        Report.user_id == str(current_user.id),
        Report.status == ReportStatus.FAILED
    ).count()
    scheduled_reports = await Report.find(
        Report.user_id == str(current_user.id),
        Report.is_scheduled == True
    ).count()
    
    # Get total downloads
    reports_with_downloads = await Report.find(
        Report.user_id == str(current_user.id)
    ).to_list()
    total_downloads = sum(report.download_count for report in reports_with_downloads)
    
    # Get recent reports
    recent_reports = await Report.find(
        Report.user_id == str(current_user.id)
    ).sort(-Report.created_at).limit(5).to_list()
    
    recent_reports_response = [
        ReportResponse(
            id=str(report.id),
            title=report.title,
            description=report.description,
            report_type=report.report_type,
            page_ids=report.page_ids,
            date_from=report.date_from,
            date_to=report.date_to,
            format=report.format,
            status=report.status,
            progress=report.progress,
            file_url=str(report.file_url) if report.file_url else None,
            file_size=report.file_size,
            download_count=report.download_count,
            error_message=report.error_message,
            is_scheduled=report.is_scheduled,
            frequency=report.frequency,
            next_generation=report.next_generation,
            last_generated=report.last_generated,
            created_at=report.created_at,
            updated_at=report.updated_at,
            expires_at=report.expires_at
        )
        for report in recent_reports
    ]
    
    return ReportSummary(
        total_reports=total_reports,
        pending_reports=pending_reports,
        completed_reports=completed_reports,
        failed_reports=failed_reports,
        scheduled_reports=scheduled_reports,
        total_downloads=total_downloads,
        recent_reports=recent_reports_response
    )


async def generate_report_task(report_id: str):
    """Background task to generate a report."""
    try:
        report = await Report.get(report_id)
        if not report:
            return
        
        # Update status to generating
        report.update_progress(10, ReportStatus.GENERATING)
        await report.save()
        
        # Simulate report generation
        import asyncio
        await asyncio.sleep(2)  # Simulate processing time
        
        report.update_progress(50)
        await report.save()
        
        await asyncio.sleep(2)  # More processing
        
        # Mark as completed
        file_url = f"https://example.com/reports/{report_id}.{report.format}"
        report.mark_completed(file_url, 1024 * 100)  # 100KB file
        await report.save()
        
        logger.info(f"Report generated successfully: {report_id}")
        
    except Exception as e:
        # Mark as failed
        report = await Report.get(report_id)
        if report:
            report.mark_failed(str(e))
            await report.save()
        
        logger.error(f"Report generation failed: {report_id}, error: {e}")