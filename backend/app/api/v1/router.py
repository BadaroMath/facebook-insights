"""
Main API router that includes all endpoint routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    facebook_pages,
    facebook_posts,
    analytics,
    reports,
    health,
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    facebook_pages.router,
    prefix="/pages",
    tags=["Facebook Pages"]
)

api_router.include_router(
    facebook_posts.router,
    prefix="/posts",
    tags=["Facebook Posts"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"]
)

api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"]
)

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health Check"]
)