"""
Facebook Post model for storing post information and metrics.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field, HttpUrl
from beanie import Document, Indexed
from pymongo import IndexModel
from enum import Enum


class PostType(str, Enum):
    """Facebook post types."""
    PHOTO = "photo"
    VIDEO = "video"
    LINK = "link"
    STATUS = "status"
    EVENT = "event"
    OFFER = "offer"


class FacebookPost(Document):
    """Facebook Post document model."""
    
    # Post identification
    post_id: Indexed(str, unique=True)
    page_id: Indexed(str)
    
    # Post content
    message: Optional[str] = None
    story: Optional[str] = None
    description: Optional[str] = None
    caption: Optional[str] = None
    
    # Post metadata
    post_type: PostType = PostType.STATUS
    status_type: Optional[str] = None
    
    # Media information
    full_picture: Optional[HttpUrl] = None
    picture: Optional[HttpUrl] = None
    source: Optional[HttpUrl] = None  # For videos
    
    # Links and external content
    link: Optional[HttpUrl] = None
    name: Optional[str] = None  # Link title
    
    # Timing
    created_time: Indexed(datetime)
    updated_time: Optional[datetime] = None
    
    # Publishing information
    is_published: bool = True
    is_hidden: bool = False
    is_expired: bool = False
    
    # Author information
    from_user: Optional[Dict[str, Any]] = None
    
    # Targeting and promotion
    targeting: Optional[Dict[str, Any]] = None
    promotion_status: Optional[str] = None
    
    # Actions (like, comment, share buttons)
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Privacy settings
    privacy: Optional[Dict[str, str]] = None
    
    # Video-specific fields
    video_id: Optional[str] = None
    video_length: Optional[int] = None  # seconds
    
    # Engagement metrics (cached from insights)
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    reactions_count: int = 0
    
    # Reach and impressions (cached from insights)
    reach: int = 0
    impressions: int = 0
    engagement_rate: float = 0.0
    
    # Detailed reactions
    reactions_like: int = 0
    reactions_love: int = 0
    reactions_wow: int = 0
    reactions_haha: int = 0
    reactions_sad: int = 0
    reactions_angry: int = 0
    
    # Video metrics
    video_views: int = 0
    video_views_unique: int = 0
    video_avg_time_watched: float = 0.0
    video_complete_views: int = 0
    
    # Click metrics
    clicks: int = 0
    clicks_unique: int = 0
    
    # Negative feedback
    negative_feedback: int = 0
    negative_feedback_unique: int = 0
    
    # Sync tracking
    last_insights_sync: Optional[datetime] = None
    insights_sync_errors: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "facebook_posts"
        indexes = [
            IndexModel("post_id", unique=True),
            IndexModel("page_id"),
            IndexModel("created_time"),
            IndexModel([("page_id", 1), ("created_time", -1)]),
            IndexModel("post_type"),
            IndexModel("is_published"),
            IndexModel("engagement_rate"),
        ]
    
    def __str__(self):
        return f"FacebookPost(post_id={self.post_id}, created_time={self.created_time})"
    
    def calculate_engagement_rate(self) -> float:
        """Calculate engagement rate based on reach."""
        if self.reach == 0:
            return 0.0
        
        total_engagement = (
            self.likes_count + 
            self.comments_count + 
            self.shares_count + 
            self.clicks
        )
        
        return (total_engagement / self.reach) * 100
    
    def update_engagement_metrics(self):
        """Update calculated engagement metrics."""
        self.engagement_rate = self.calculate_engagement_rate()
        self.reactions_count = (
            self.reactions_like +
            self.reactions_love +
            self.reactions_wow +
            self.reactions_haha +
            self.reactions_sad +
            self.reactions_angry
        )
        self.updated_at = datetime.utcnow()
    
    def update_insights_sync(self):
        """Update insights sync timestamp."""
        self.last_insights_sync = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def record_insights_error(self):
        """Record insights sync error."""
        self.insights_sync_errors += 1
        self.updated_at = datetime.utcnow()
    
    def get_content_preview(self, max_length: int = 100) -> str:
        """Get a preview of the post content."""
        content = self.message or self.story or self.description or self.caption or ""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."
    
    def is_video_post(self) -> bool:
        """Check if this is a video post."""
        return self.post_type == PostType.VIDEO or self.video_id is not None
    
    def get_primary_image(self) -> Optional[str]:
        """Get the primary image URL for this post."""
        return str(self.full_picture) if self.full_picture else str(self.picture) if self.picture else None


class FacebookPostCreate(Document):
    """Schema for creating Facebook posts."""
    post_id: str
    page_id: str
    message: Optional[str] = None
    post_type: PostType = PostType.STATUS
    created_time: datetime


class FacebookPostUpdate(Document):
    """Schema for updating Facebook posts."""
    message: Optional[str] = None
    description: Optional[str] = None
    is_published: Optional[bool] = None
    is_hidden: Optional[bool] = None


class FacebookPostResponse(Document):
    """Schema for Facebook post responses."""
    id: str
    post_id: str
    page_id: str
    message: Optional[str] = None
    post_type: PostType
    created_time: datetime
    full_picture: Optional[str] = None
    likes_count: int
    comments_count: int
    shares_count: int
    reach: int
    impressions: int
    engagement_rate: float
    is_published: bool
    created_at: datetime
    updated_at: datetime


class PostMetrics(Document):
    """Post performance metrics."""
    post_id: str
    likes: int
    comments: int
    shares: int
    reactions: int
    reach: int
    impressions: int
    clicks: int
    engagement_rate: float
    video_views: Optional[int] = None
    video_completion_rate: Optional[float] = None
    timestamp: datetime


class PostPerformanceSummary(Document):
    """Post performance summary for analytics."""
    page_id: str
    period_start: datetime
    period_end: datetime
    total_posts: int
    avg_engagement_rate: float
    total_reach: int
    total_impressions: int
    total_likes: int
    total_comments: int
    total_shares: int
    best_performing_post_id: Optional[str] = None
    worst_performing_post_id: Optional[str] = None