"""
Facebook Pages management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.user import User
from app.models.facebook_page import FacebookPage, FacebookPageCreate, FacebookPageUpdate, FacebookPageResponse
from app.api.v1.endpoints.auth import get_current_user
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=List[FacebookPageResponse], summary="Get user's Facebook pages")
async def get_pages(
    current_user: User = Depends(get_current_user),
    active_only: bool = Query(True, description="Return only active pages")
) -> List[FacebookPageResponse]:
    """Get all Facebook pages connected by the current user."""
    
    query = FacebookPage.find(FacebookPage.user_id == str(current_user.id))
    
    if active_only:
        query = query.find(FacebookPage.is_active == True)
    
    pages = await query.to_list()
    
    return [
        FacebookPageResponse(
            id=str(page.id),
            page_id=page.page_id,
            name=page.name,
            username=page.username,
            about=page.about,
            category=page.category,
            website=str(page.website) if page.website else None,
            link=str(page.link) if page.link else None,
            picture_url=str(page.picture_url) if page.picture_url else None,
            fan_count=page.fan_count,
            followers_count=page.followers_count,
            talking_about_count=page.talking_about_count,
            is_active=page.is_active,
            sync_enabled=page.sync_enabled,
            last_sync_at=page.last_sync_at,
            sync_frequency=page.sync_frequency,
            total_posts_synced=page.total_posts_synced,
            sync_errors=page.sync_errors,
            last_error=page.last_error,
            created_at=page.created_at,
            updated_at=page.updated_at
        )
        for page in pages
    ]


@router.post("/", response_model=FacebookPageResponse, summary="Add Facebook page")
async def add_page(
    page_data: FacebookPageCreate,
    current_user: User = Depends(get_current_user)
) -> FacebookPageResponse:
    """Add a new Facebook page for the current user."""
    
    # Check if page already exists
    existing_page = await FacebookPage.find_one(FacebookPage.page_id == page_data.page_id)
    if existing_page:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page already exists"
        )
    
    # TODO: Verify the access token and get page information from Facebook API
    # For now, create a basic page entry
    page = FacebookPage(
        page_id=page_data.page_id,
        user_id=str(current_user.id),
        name=f"Page {page_data.page_id}",  # This should come from Facebook API
        access_token=page_data.access_token,
        sync_enabled=page_data.sync_enabled,
        posts_sync_days=page_data.posts_sync_days,
        insights_sync_days=page_data.insights_sync_days
    )
    
    await page.save()
    
    # Update user's connected pages count
    current_user.increment_pages_connected()
    await current_user.save()
    
    logger.info(f"Facebook page added: {page.page_id} for user {current_user.email}")
    
    return FacebookPageResponse(
        id=str(page.id),
        page_id=page.page_id,
        name=page.name,
        username=page.username,
        about=page.about,
        category=page.category,
        website=str(page.website) if page.website else None,
        link=str(page.link) if page.link else None,
        picture_url=str(page.picture_url) if page.picture_url else None,
        fan_count=page.fan_count,
        followers_count=page.followers_count,
        talking_about_count=page.talking_about_count,
        is_active=page.is_active,
        sync_enabled=page.sync_enabled,
        last_sync_at=page.last_sync_at,
        sync_frequency=page.sync_frequency,
        total_posts_synced=page.total_posts_synced,
        sync_errors=page.sync_errors,
        last_error=page.last_error,
        created_at=page.created_at,
        updated_at=page.updated_at
    )


@router.get("/{page_id}", response_model=FacebookPageResponse, summary="Get Facebook page details")
async def get_page(
    page_id: str,
    current_user: User = Depends(get_current_user)
) -> FacebookPageResponse:
    """Get details of a specific Facebook page."""
    
    page = await FacebookPage.find_one(
        FacebookPage.page_id == page_id,
        FacebookPage.user_id == str(current_user.id)
    )
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )
    
    return FacebookPageResponse(
        id=str(page.id),
        page_id=page.page_id,
        name=page.name,
        username=page.username,
        about=page.about,
        category=page.category,
        website=str(page.website) if page.website else None,
        link=str(page.link) if page.link else None,
        picture_url=str(page.picture_url) if page.picture_url else None,
        fan_count=page.fan_count,
        followers_count=page.followers_count,
        talking_about_count=page.talking_about_count,
        is_active=page.is_active,
        sync_enabled=page.sync_enabled,
        last_sync_at=page.last_sync_at,
        sync_frequency=page.sync_frequency,
        total_posts_synced=page.total_posts_synced,
        sync_errors=page.sync_errors,
        last_error=page.last_error,
        created_at=page.created_at,
        updated_at=page.updated_at
    )


@router.put("/{page_id}", response_model=FacebookPageResponse, summary="Update Facebook page settings")
async def update_page(
    page_id: str,
    page_update: FacebookPageUpdate,
    current_user: User = Depends(get_current_user)
) -> FacebookPageResponse:
    """Update Facebook page settings."""
    
    page = await FacebookPage.find_one(
        FacebookPage.page_id == page_id,
        FacebookPage.user_id == str(current_user.id)
    )
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )
    
    # Update fields that are provided
    update_data = page_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(page, field, value)
    
    await page.save()
    logger.info(f"Facebook page updated: {page.page_id}")
    
    return FacebookPageResponse(
        id=str(page.id),
        page_id=page.page_id,
        name=page.name,
        username=page.username,
        about=page.about,
        category=page.category,
        website=str(page.website) if page.website else None,
        link=str(page.link) if page.link else None,
        picture_url=str(page.picture_url) if page.picture_url else None,
        fan_count=page.fan_count,
        followers_count=page.followers_count,
        talking_about_count=page.talking_about_count,
        is_active=page.is_active,
        sync_enabled=page.sync_enabled,
        last_sync_at=page.last_sync_at,
        sync_frequency=page.sync_frequency,
        total_posts_synced=page.total_posts_synced,
        sync_errors=page.sync_errors,
        last_error=page.last_error,
        created_at=page.created_at,
        updated_at=page.updated_at
    )


@router.delete("/{page_id}", summary="Remove Facebook page")
async def remove_page(
    page_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a Facebook page from the user's account."""
    
    page = await FacebookPage.find_one(
        FacebookPage.page_id == page_id,
        FacebookPage.user_id == str(current_user.id)
    )
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )
    
    await page.delete()
    logger.info(f"Facebook page removed: {page_id} for user {current_user.email}")
    
    return {"message": "Page successfully removed"}


@router.post("/{page_id}/sync", summary="Trigger page data sync")
async def sync_page(
    page_id: str,
    current_user: User = Depends(get_current_user)
):
    """Trigger manual data synchronization for a Facebook page."""
    
    page = await FacebookPage.find_one(
        FacebookPage.page_id == page_id,
        FacebookPage.user_id == str(current_user.id)
    )
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found"
        )
    
    if not page.is_active or not page.sync_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page sync is disabled"
        )
    
    # TODO: Trigger background sync task
    logger.info(f"Manual sync triggered for page: {page_id}")
    
    return {"message": "Sync triggered successfully", "page_id": page_id}