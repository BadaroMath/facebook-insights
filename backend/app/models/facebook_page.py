"""
Facebook Page model for storing page information and settings.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field, HttpUrl
from beanie import Document, Indexed
from pymongo import IndexModel


class FacebookPage(Document):
    """Facebook Page document model."""
    
    # Page identification
    page_id: Indexed(str, unique=True)
    user_id: Indexed(str)  # Owner user ID
    
    # Basic page information
    name: str
    username: Optional[str] = None
    about: Optional[str] = None
    category: Optional[str] = None
    website: Optional[HttpUrl] = None
    
    # Page URLs and links
    link: Optional[HttpUrl] = None
    picture_url: Optional[HttpUrl] = None
    cover_photo_url: Optional[HttpUrl] = None
    
    # Page statistics
    fan_count: int = 0
    followers_count: int = 0
    talking_about_count: int = 0
    checkins: int = 0
    
    # Access token for this page
    access_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    # Sync settings
    is_active: bool = True
    sync_enabled: bool = True
    last_sync_at: Optional[datetime] = None
    sync_frequency: int = 60  # minutes
    
    # Data ranges
    posts_sync_days: int = 30  # How many days of posts to sync
    insights_sync_days: int = 30  # How many days of insights to sync
    
    # Page permissions
    permissions: List[str] = Field(default_factory=list)
    
    # Metadata
    location: Optional[Dict[str, Any]] = None
    hours: Optional[Dict[str, Any]] = None
    phone: Optional[str] = None
    
    # Statistics tracking
    total_posts_synced: int = 0
    last_post_sync_at: Optional[datetime] = None
    sync_errors: int = 0
    last_error: Optional[str] = None
    last_error_at: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "facebook_pages"
        indexes = [
            IndexModel("page_id", unique=True),
            IndexModel("user_id"),
            IndexModel([("user_id", 1), ("page_id", 1)]),
            IndexModel("is_active"),
            IndexModel("sync_enabled"),
            IndexModel("last_sync_at"),
        ]
    
    def __str__(self):
        return f"FacebookPage(page_id={self.page_id}, name={self.name})"
    
    def update_sync_time(self):
        """Update last sync timestamp."""
        self.last_sync_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def increment_posts_synced(self, count: int = 1):
        """Increment posts synced counter."""
        self.total_posts_synced += count
        self.last_post_sync_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def record_sync_error(self, error_message: str):
        """Record sync error."""
        self.sync_errors += 1
        self.last_error = error_message
        self.last_error_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def clear_sync_errors(self):
        """Clear sync error information."""
        self.sync_errors = 0
        self.last_error = None
        self.last_error_at = None
        self.updated_at = datetime.utcnow()
    
    def is_token_valid(self) -> bool:
        """Check if access token is still valid."""
        return (
            self.access_token is not None and
            self.token_expires_at is not None and
            self.token_expires_at > datetime.utcnow()
        )
    
    def needs_sync(self) -> bool:
        """Check if page needs to be synced."""
        if not self.sync_enabled or not self.is_active:
            return False
        
        if self.last_sync_at is None:
            return True
        
        time_since_sync = datetime.utcnow() - self.last_sync_at
        return time_since_sync.total_seconds() >= (self.sync_frequency * 60)


class FacebookPageCreate(Document):
    """Schema for adding new Facebook pages."""
    page_id: str
    access_token: str
    sync_enabled: bool = True
    posts_sync_days: int = 30
    insights_sync_days: int = 30


class FacebookPageUpdate(Document):
    """Schema for updating Facebook page settings."""
    sync_enabled: Optional[bool] = None
    sync_frequency: Optional[int] = None
    posts_sync_days: Optional[int] = None
    insights_sync_days: Optional[int] = None


class FacebookPageResponse(Document):
    """Schema for Facebook page responses."""
    id: str
    page_id: str
    name: str
    username: Optional[str] = None
    about: Optional[str] = None
    category: Optional[str] = None
    website: Optional[str] = None
    link: Optional[str] = None
    picture_url: Optional[str] = None
    fan_count: int
    followers_count: int
    talking_about_count: int
    is_active: bool
    sync_enabled: bool
    last_sync_at: Optional[datetime] = None
    sync_frequency: int
    total_posts_synced: int
    sync_errors: int
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FacebookPageStats(Document):
    """Facebook page statistics summary."""
    page_id: str
    name: str
    fan_count: int
    followers_count: int
    posts_count: int
    avg_engagement_rate: float
    total_reach: int
    total_impressions: int
    period_start: datetime
    period_end: datetime