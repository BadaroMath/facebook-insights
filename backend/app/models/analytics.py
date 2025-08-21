"""
Analytics model for storing processed Facebook insights and metrics.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from pydantic import Field
from beanie import Document, Indexed
from pymongo import IndexModel
from enum import Enum


class MetricType(str, Enum):
    """Types of analytics metrics."""
    PAGE_DAILY = "page_daily"
    PAGE_LIFETIME = "page_lifetime"
    POST_LIFETIME = "post_lifetime"
    VIDEO_METRICS = "video_metrics"


class Analytics(Document):
    """Analytics document model for storing Facebook insights."""
    
    # Identification
    page_id: Optional[Indexed(str)] = None
    post_id: Optional[Indexed(str)] = None
    metric_type: MetricType
    
    # Time dimension
    date: Indexed(date)
    period: str = "day"  # day, week, days_28, lifetime
    
    # Page-level metrics
    page_impressions: Optional[int] = None
    page_impressions_unique: Optional[int] = None
    page_impressions_paid: Optional[int] = None
    page_impressions_paid_unique: Optional[int] = None
    page_impressions_organic: Optional[int] = None
    page_impressions_organic_unique: Optional[int] = None
    page_impressions_viral: Optional[int] = None
    page_impressions_viral_unique: Optional[int] = None
    
    # Page engagement metrics
    page_engaged_users: Optional[int] = None
    page_post_engagements: Optional[int] = None
    page_consumptions: Optional[int] = None
    page_consumptions_unique: Optional[int] = None
    page_negative_feedback: Optional[int] = None
    page_negative_feedback_unique: Optional[int] = None
    
    # Page views and actions
    page_views_total: Optional[int] = None
    page_total_actions: Optional[int] = None
    page_video_views: Optional[int] = None
    
    # Page followers
    page_daily_follows_unique: Optional[int] = None
    page_fan_count: Optional[int] = None
    
    # Page messages
    page_messages_new_conversations_unique: Optional[int] = None
    
    # Page posts metrics
    page_posts_impressions: Optional[int] = None
    page_posts_impressions_unique: Optional[int] = None
    page_posts_impressions_paid: Optional[int] = None
    page_posts_impressions_paid_unique: Optional[int] = None
    page_posts_impressions_organic: Optional[int] = None
    page_posts_impressions_organic_unique: Optional[int] = None
    page_posts_impressions_viral: Optional[int] = None
    page_posts_impressions_viral_unique: Optional[int] = None
    page_posts_impressions_nonviral: Optional[int] = None
    page_posts_impressions_nonviral_unique: Optional[int] = None
    
    # Page reactions
    page_actions_post_reactions_like_total: Optional[int] = None
    page_actions_post_reactions_love_total: Optional[int] = None
    page_actions_post_reactions_wow_total: Optional[int] = None
    page_actions_post_reactions_haha_total: Optional[int] = None
    page_actions_post_reactions_sorry_total: Optional[int] = None
    page_actions_post_reactions_anger_total: Optional[int] = None
    
    # Post-level metrics
    post_impressions: Optional[int] = None
    post_impressions_unique: Optional[int] = None
    post_impressions_paid: Optional[int] = None
    post_impressions_paid_unique: Optional[int] = None
    post_impressions_fan: Optional[int] = None
    post_impressions_fan_unique: Optional[int] = None
    post_impressions_fan_paid: Optional[int] = None
    post_impressions_fan_paid_unique: Optional[int] = None
    post_impressions_organic: Optional[int] = None
    post_impressions_organic_unique: Optional[int] = None
    post_impressions_viral: Optional[int] = None
    post_impressions_viral_unique: Optional[int] = None
    post_impressions_nonviral: Optional[int] = None
    post_impressions_nonviral_unique: Optional[int] = None
    
    # Post engagement
    post_engaged_users: Optional[int] = None
    post_engaged_fan: Optional[int] = None
    post_clicks: Optional[int] = None
    post_clicks_unique: Optional[int] = None
    
    # Post reactions
    post_reactions_like_total: Optional[int] = None
    post_reactions_love_total: Optional[int] = None
    post_reactions_wow_total: Optional[int] = None
    post_reactions_haha_total: Optional[int] = None
    post_reactions_sorry_total: Optional[int] = None
    post_reactions_anger_total: Optional[int] = None
    
    # Post negative feedback
    post_negative_feedback: Optional[int] = None
    post_negative_feedback_unique: Optional[int] = None
    
    # Video metrics
    post_video_avg_time_watched: Optional[float] = None
    post_video_complete_views_organic: Optional[int] = None
    post_video_complete_views_organic_unique: Optional[int] = None
    post_video_complete_views_paid: Optional[int] = None
    post_video_complete_views_paid_unique: Optional[int] = None
    post_video_views_organic: Optional[int] = None
    post_video_views_organic_unique: Optional[int] = None
    post_video_views_paid: Optional[int] = None
    post_video_views_paid_unique: Optional[int] = None
    post_video_length: Optional[int] = None
    post_video_views: Optional[int] = None
    post_video_views_unique: Optional[int] = None
    
    # Calculated metrics
    engagement_rate: Optional[float] = None
    reach_rate: Optional[float] = None
    virality_rate: Optional[float] = None
    
    # Raw data for debugging
    raw_data: Optional[Dict[str, Any]] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "analytics"
        indexes = [
            IndexModel([("page_id", 1), ("date", -1)]),
            IndexModel([("post_id", 1), ("date", -1)]),
            IndexModel("date"),
            IndexModel("metric_type"),
            IndexModel([("page_id", 1), ("metric_type", 1), ("date", -1)]),
        ]
    
    def __str__(self):
        return f"Analytics(type={self.metric_type}, date={self.date})"
    
    def calculate_engagement_rate(self) -> float:
        """Calculate engagement rate based on available metrics."""
        if self.metric_type == MetricType.POST_LIFETIME and self.post_impressions:
            total_engagement = sum(filter(None, [
                self.post_reactions_like_total,
                self.post_reactions_love_total,
                self.post_reactions_wow_total,
                self.post_reactions_haha_total,
                self.post_reactions_sorry_total,
                self.post_reactions_anger_total,
                self.post_clicks,
            ]))
            return (total_engagement / self.post_impressions) * 100 if self.post_impressions > 0 else 0.0
        
        elif self.metric_type == MetricType.PAGE_DAILY and self.page_impressions:
            total_engagement = sum(filter(None, [
                self.page_engaged_users,
                self.page_post_engagements,
            ]))
            return (total_engagement / self.page_impressions) * 100 if self.page_impressions > 0 else 0.0
        
        return 0.0
    
    def calculate_reach_rate(self) -> float:
        """Calculate reach rate (unique impressions / total impressions)."""
        if self.metric_type == MetricType.POST_LIFETIME:
            if self.post_impressions and self.post_impressions_unique:
                return (self.post_impressions_unique / self.post_impressions) * 100
        elif self.metric_type == MetricType.PAGE_DAILY:
            if self.page_impressions and self.page_impressions_unique:
                return (self.page_impressions_unique / self.page_impressions) * 100
        return 0.0
    
    def calculate_virality_rate(self) -> float:
        """Calculate virality rate (viral impressions / total impressions)."""
        if self.metric_type == MetricType.POST_LIFETIME:
            if self.post_impressions and self.post_impressions_viral:
                return (self.post_impressions_viral / self.post_impressions) * 100
        elif self.metric_type == MetricType.PAGE_DAILY:
            if self.page_impressions and self.page_impressions_viral:
                return (self.page_impressions_viral / self.page_impressions) * 100
        return 0.0
    
    def update_calculated_metrics(self):
        """Update all calculated metrics."""
        self.engagement_rate = self.calculate_engagement_rate()
        self.reach_rate = self.calculate_reach_rate()
        self.virality_rate = self.calculate_virality_rate()
        self.updated_at = datetime.utcnow()
    
    @classmethod
    async def get_page_analytics_summary(cls, page_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get analytics summary for a page within date range."""
        pipeline = [
            {
                "$match": {
                    "page_id": page_id,
                    "date": {"$gte": start_date, "$lte": end_date},
                    "metric_type": MetricType.PAGE_DAILY
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_impressions": {"$sum": "$page_impressions"},
                    "total_reach": {"$sum": "$page_impressions_unique"},
                    "total_engagement": {"$sum": "$page_engaged_users"},
                    "total_video_views": {"$sum": "$page_video_views"},
                    "avg_engagement_rate": {"$avg": "$engagement_rate"},
                    "days_count": {"$sum": 1}
                }
            }
        ]
        
        result = await cls.aggregate(pipeline).to_list()
        return result[0] if result else {}


class AnalyticsCreate(Document):
    """Schema for creating analytics records."""
    page_id: Optional[str] = None
    post_id: Optional[str] = None
    metric_type: MetricType
    date: date
    raw_data: Dict[str, Any]


class AnalyticsResponse(Document):
    """Schema for analytics responses."""
    id: str
    page_id: Optional[str] = None
    post_id: Optional[str] = None
    metric_type: MetricType
    date: date
    period: str
    engagement_rate: Optional[float] = None
    reach_rate: Optional[float] = None
    virality_rate: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class AnalyticsSummary(Document):
    """Analytics summary for dashboards."""
    page_id: str
    period_start: date
    period_end: date
    total_impressions: int
    total_reach: int
    total_engagement: int
    avg_engagement_rate: float
    total_posts: int
    growth_rate: float
    top_performing_day: Optional[date] = None
    metrics: Dict[str, Any]


class InsightMetric(Document):
    """Individual insight metric."""
    name: str
    period: str
    values: List[Dict[str, Any]]
    title: Optional[str] = None
    description: Optional[str] = None