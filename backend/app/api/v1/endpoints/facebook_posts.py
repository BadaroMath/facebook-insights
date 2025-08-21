"""
Facebook Posts endpoints.
"""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.user import User
from app.models.facebook_post import FacebookPost, FacebookPostResponse, PostType
from app.api.v1.endpoints.auth import get_current_user
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=List[FacebookPostResponse], summary="Get Facebook posts")
async def get_posts(
    current_user: User = Depends(get_current_user),
    page_id: Optional[str] = Query(None, description="Filter by page ID"),
    post_type: Optional[PostType] = Query(None, description="Filter by post type"),
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    limit: int = Query(50, le=100, description="Number of posts to return"),
    skip: int = Query(0, description="Number of posts to skip")
) -> List[FacebookPostResponse]:
    """Get Facebook posts with optional filtering."""
    
    # Build query
    query = FacebookPost.find()
    
    if page_id:
        query = query.find(FacebookPost.page_id == page_id)
    
    if post_type:
        query = query.find(FacebookPost.post_type == post_type)
    
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.find(FacebookPost.created_time >= start_datetime)
    
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.find(FacebookPost.created_time <= end_datetime)
    
    # Sort by creation time (newest first)
    query = query.sort(-FacebookPost.created_time)
    
    # Apply pagination
    posts = await query.skip(skip).limit(limit).to_list()
    
    return [
        FacebookPostResponse(
            id=str(post.id),
            post_id=post.post_id,
            page_id=post.page_id,
            message=post.message,
            post_type=post.post_type,
            created_time=post.created_time,
            full_picture=str(post.full_picture) if post.full_picture else None,
            likes_count=post.likes_count,
            comments_count=post.comments_count,
            shares_count=post.shares_count,
            reach=post.reach,
            impressions=post.impressions,
            engagement_rate=post.engagement_rate,
            is_published=post.is_published,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
        for post in posts
    ]


@router.get("/{post_id}", response_model=FacebookPostResponse, summary="Get Facebook post details")
async def get_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
) -> FacebookPostResponse:
    """Get details of a specific Facebook post."""
    
    post = await FacebookPost.find_one(FacebookPost.post_id == post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return FacebookPostResponse(
        id=str(post.id),
        post_id=post.post_id,
        page_id=post.page_id,
        message=post.message,
        post_type=post.post_type,
        created_time=post.created_time,
        full_picture=str(post.full_picture) if post.full_picture else None,
        likes_count=post.likes_count,
        comments_count=post.comments_count,
        shares_count=post.shares_count,
        reach=post.reach,
        impressions=post.impressions,
        engagement_rate=post.engagement_rate,
        is_published=post.is_published,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


@router.get("/page/{page_id}", response_model=List[FacebookPostResponse], summary="Get posts by page")
async def get_posts_by_page(
    page_id: str,
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, le=100, description="Number of posts to return"),
    skip: int = Query(0, description="Number of posts to skip")
) -> List[FacebookPostResponse]:
    """Get all posts for a specific Facebook page."""
    
    posts = await FacebookPost.find(
        FacebookPost.page_id == page_id
    ).sort(-FacebookPost.created_time).skip(skip).limit(limit).to_list()
    
    return [
        FacebookPostResponse(
            id=str(post.id),
            post_id=post.post_id,
            page_id=post.page_id,
            message=post.message,
            post_type=post.post_type,
            created_time=post.created_time,
            full_picture=str(post.full_picture) if post.full_picture else None,
            likes_count=post.likes_count,
            comments_count=post.comments_count,
            shares_count=post.shares_count,
            reach=post.reach,
            impressions=post.impressions,
            engagement_rate=post.engagement_rate,
            is_published=post.is_published,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
        for post in posts
    ]


@router.get("/page/{page_id}/top-performing", response_model=List[FacebookPostResponse], summary="Get top performing posts")
async def get_top_performing_posts(
    page_id: str,
    current_user: User = Depends(get_current_user),
    metric: str = Query("engagement_rate", description="Metric to sort by"),
    limit: int = Query(10, le=50, description="Number of posts to return"),
    days: int = Query(30, description="Number of days to look back")
) -> List[FacebookPostResponse]:
    """Get top performing posts for a page based on specified metric."""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Build query based on metric
    query = FacebookPost.find(
        FacebookPost.page_id == page_id,
        FacebookPost.created_time >= start_date,
        FacebookPost.created_time <= end_date
    )
    
    # Sort by the specified metric
    if metric == "engagement_rate":
        query = query.sort(-FacebookPost.engagement_rate)
    elif metric == "reach":
        query = query.sort(-FacebookPost.reach)
    elif metric == "impressions":
        query = query.sort(-FacebookPost.impressions)
    elif metric == "likes":
        query = query.sort(-FacebookPost.likes_count)
    else:
        query = query.sort(-FacebookPost.engagement_rate)  # Default
    
    posts = await query.limit(limit).to_list()
    
    return [
        FacebookPostResponse(
            id=str(post.id),
            post_id=post.post_id,
            page_id=post.page_id,
            message=post.message,
            post_type=post.post_type,
            created_time=post.created_time,
            full_picture=str(post.full_picture) if post.full_picture else None,
            likes_count=post.likes_count,
            comments_count=post.comments_count,
            shares_count=post.shares_count,
            reach=post.reach,
            impressions=post.impressions,
            engagement_rate=post.engagement_rate,
            is_published=post.is_published,
            created_at=post.created_at,
            updated_at=post.updated_at
        )
        for post in posts
    ]