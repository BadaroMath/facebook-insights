"""
Report model for storing generated reports and scheduled exports.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import Field, HttpUrl
from beanie import Document, Indexed
from pymongo import IndexModel
from enum import Enum


class ReportType(str, Enum):
    """Types of reports."""
    PAGE_PERFORMANCE = "page_performance"
    POST_ANALYSIS = "post_analysis"
    ENGAGEMENT_SUMMARY = "engagement_summary"
    GROWTH_REPORT = "growth_report"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """Report output formats."""
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"


class ReportStatus(str, Enum):
    """Report generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class ReportFrequency(str, Enum):
    """Report scheduling frequency."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class Report(Document):
    """Report document model."""
    
    # Basic information
    user_id: Indexed(str)
    title: str
    description: Optional[str] = None
    report_type: ReportType
    
    # Configuration
    page_ids: List[str] = Field(default_factory=list)
    date_from: date
    date_to: date
    
    # Filters and parameters
    filters: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Output settings
    format: ReportFormat = ReportFormat.PDF
    include_charts: bool = True
    include_raw_data: bool = False
    
    # Scheduling
    is_scheduled: bool = False
    frequency: Optional[ReportFrequency] = None
    next_generation: Optional[datetime] = None
    last_generated: Optional[datetime] = None
    
    # Generation status
    status: ReportStatus = ReportStatus.PENDING
    progress: int = 0  # 0-100
    
    # Results
    file_url: Optional[HttpUrl] = None
    file_size: Optional[int] = None  # bytes
    download_count: int = 0
    
    # Error information
    error_message: Optional[str] = None
    generation_time: Optional[float] = None  # seconds
    
    # Email settings
    email_recipients: List[str] = Field(default_factory=list)
    email_sent: bool = False
    email_sent_at: Optional[datetime] = None
    
    # Report content (for preview)
    summary: Optional[Dict[str, Any]] = None
    charts_data: Optional[List[Dict[str, Any]]] = None
    
    # Metadata
    template_used: Optional[str] = None
    version: str = "1.0"
    tags: List[str] = Field(default_factory=list)
    
    # Expiration
    expires_at: Optional[datetime] = None
    auto_delete_after_days: int = 30
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "reports"
        indexes = [
            IndexModel("user_id"),
            IndexModel("created_at"),
            IndexModel([("user_id", 1), ("created_at", -1)]),
            IndexModel("status"),
            IndexModel("report_type"),
            IndexModel("next_generation", sparse=True),
            IndexModel("expires_at", expireAfterSeconds=0),
        ]
    
    def __str__(self):
        return f"Report(title={self.title}, type={self.report_type})"
    
    def update_progress(self, progress: int, status: Optional[ReportStatus] = None):
        """Update report generation progress."""
        self.progress = max(0, min(100, progress))
        if status:
            self.status = status
        self.updated_at = datetime.utcnow()
    
    def mark_completed(self, file_url: str, file_size: int = None):
        """Mark report as completed."""
        self.status = ReportStatus.COMPLETED
        self.progress = 100
        self.file_url = file_url
        self.file_size = file_size
        self.last_generated = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Set expiration
        if self.auto_delete_after_days > 0:
            from datetime import timedelta
            self.expires_at = datetime.utcnow() + timedelta(days=self.auto_delete_after_days)
    
    def mark_failed(self, error_message: str):
        """Mark report generation as failed."""
        self.status = ReportStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.utcnow()
    
    def increment_download_count(self):
        """Increment download counter."""
        self.download_count += 1
        self.updated_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if report has expired."""
        return self.expires_at is not None and datetime.utcnow() > self.expires_at
    
    def can_be_downloaded(self) -> bool:
        """Check if report can be downloaded."""
        return (
            self.status == ReportStatus.COMPLETED and
            self.file_url is not None and
            not self.is_expired()
        )
    
    def schedule_next_generation(self):
        """Schedule next report generation based on frequency."""
        if not self.is_scheduled or not self.frequency:
            return
        
        from datetime import timedelta
        
        now = datetime.utcnow()
        
        if self.frequency == ReportFrequency.DAILY:
            self.next_generation = now + timedelta(days=1)
        elif self.frequency == ReportFrequency.WEEKLY:
            self.next_generation = now + timedelta(weeks=1)
        elif self.frequency == ReportFrequency.MONTHLY:
            self.next_generation = now + timedelta(days=30)
        elif self.frequency == ReportFrequency.QUARTERLY:
            self.next_generation = now + timedelta(days=90)
        
        self.updated_at = datetime.utcnow()
    
    def get_date_range_display(self) -> str:
        """Get formatted date range for display."""
        return f"{self.date_from.strftime('%Y-%m-%d')} to {self.date_to.strftime('%Y-%m-%d')}"


class ReportCreate(Document):
    """Schema for creating reports."""
    title: str
    description: Optional[str] = None
    report_type: ReportType
    page_ids: List[str]
    date_from: date
    date_to: date
    format: ReportFormat = ReportFormat.PDF
    filters: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    include_charts: bool = True
    include_raw_data: bool = False
    email_recipients: Optional[List[str]] = None
    is_scheduled: bool = False
    frequency: Optional[ReportFrequency] = None


class ReportUpdate(Document):
    """Schema for updating reports."""
    title: Optional[str] = None
    description: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    email_recipients: Optional[List[str]] = None
    is_scheduled: Optional[bool] = None
    frequency: Optional[ReportFrequency] = None


class ReportResponse(Document):
    """Schema for report responses."""
    id: str
    title: str
    description: Optional[str] = None
    report_type: ReportType
    page_ids: List[str]
    date_from: date
    date_to: date
    format: ReportFormat
    status: ReportStatus
    progress: int
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    download_count: int
    error_message: Optional[str] = None
    is_scheduled: bool
    frequency: Optional[ReportFrequency] = None
    next_generation: Optional[datetime] = None
    last_generated: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None


class ReportSummary(Document):
    """Report summary for dashboard."""
    total_reports: int
    pending_reports: int
    completed_reports: int
    failed_reports: int
    scheduled_reports: int
    total_downloads: int
    recent_reports: List[ReportResponse]


class ReportTemplate(Document):
    """Report template configuration."""
    name: str
    description: str
    report_type: ReportType
    default_parameters: Dict[str, Any]
    chart_configs: List[Dict[str, Any]]
    sections: List[Dict[str, Any]]
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChartConfig(Document):
    """Chart configuration for reports."""
    chart_type: str  # line, bar, pie, etc.
    title: str
    data_source: str
    x_axis: str
    y_axis: str
    metrics: List[str]
    filters: Optional[Dict[str, Any]] = None
    styling: Optional[Dict[str, Any]] = None