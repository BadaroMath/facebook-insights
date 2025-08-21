"""
User management endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import User, UserUpdate, UserResponse
from app.api.v1.endpoints.auth import get_current_user
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/profile", response_model=UserResponse, summary="Get user profile")
async def get_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Get current user's profile information."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        avatar_url=current_user.avatar_url,
        timezone=current_user.timezone,
        language=current_user.language,
        email_notifications=current_user.email_notifications,
        marketing_emails=current_user.marketing_emails,
        last_login_at=current_user.last_login_at,
        pages_connected=current_user.pages_connected,
        reports_generated=current_user.reports_generated,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        is_facebook_connected=current_user.is_facebook_connected()
    )


@router.put("/profile", response_model=UserResponse, summary="Update user profile")
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Update current user's profile information."""
    
    # Update fields that are provided
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await current_user.save()
    logger.info(f"User profile updated: {current_user.email}")
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        avatar_url=current_user.avatar_url,
        timezone=current_user.timezone,
        language=current_user.language,
        email_notifications=current_user.email_notifications,
        marketing_emails=current_user.marketing_emails,
        last_login_at=current_user.last_login_at,
        pages_connected=current_user.pages_connected,
        reports_generated=current_user.reports_generated,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        is_facebook_connected=current_user.is_facebook_connected()
    )


@router.delete("/account", summary="Delete user account")
async def delete_account(current_user: User = Depends(get_current_user)):
    """Delete current user's account."""
    
    # In production, you should:
    # 1. Delete or anonymize associated data
    # 2. Send confirmation email
    # 3. Log the deletion for audit purposes
    
    await current_user.delete()
    logger.info(f"User account deleted: {current_user.email}")
    
    return {"message": "Account successfully deleted"}