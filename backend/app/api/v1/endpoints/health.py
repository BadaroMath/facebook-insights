"""
Health check endpoints for monitoring and load balancers.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import time
import psutil
import asyncio
from datetime import datetime

from app.core.database import database_health_check, ping_database
from app.core.config import settings

router = APIRouter()


@router.get("/", summary="Basic health check")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time()
    }


@router.get("/detailed", summary="Detailed health check")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with system information."""
    
    # Check database
    db_health = await database_health_check()
    
    # Get system information
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Check external services
    facebook_api_status = await check_facebook_api()
    
    overall_status = "healthy"
    if (
        db_health.get("status") != "healthy" or
        facebook_api_status != "healthy" or
        memory.percent > 90 or
        disk.percent > 90 or
        cpu_percent > 90
    ):
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        },
        "database": db_health,
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            }
        },
        "external_services": {
            "facebook_api": facebook_api_status
        }
    }


@router.get("/database", summary="Database health check")
async def database_health() -> Dict[str, Any]:
    """Check database connectivity and performance."""
    return await database_health_check()


@router.get("/ready", summary="Readiness probe")
async def readiness_probe() -> Dict[str, Any]:
    """Kubernetes readiness probe endpoint."""
    
    # Check critical dependencies
    db_connected = await ping_database()
    
    if not db_connected:
        raise HTTPException(status_code=503, detail="Database not ready")
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/live", summary="Liveness probe")
async def liveness_probe() -> Dict[str, Any]:
    """Kubernetes liveness probe endpoint."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


async def check_facebook_api() -> str:
    """Check Facebook Graph API connectivity."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("https://graph.facebook.com/")
            if response.status_code == 200:
                return "healthy"
            else:
                return "degraded"
    except Exception:
        return "unhealthy"


@router.get("/metrics", summary="Prometheus metrics")
async def metrics() -> str:
    """Prometheus-compatible metrics endpoint."""
    
    # Get system metrics
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_percent = psutil.cpu_percent()
    
    metrics = [
        f"# HELP facebook_analytics_memory_usage_percent Memory usage percentage",
        f"# TYPE facebook_analytics_memory_usage_percent gauge",
        f"facebook_analytics_memory_usage_percent {memory.percent}",
        f"",
        f"# HELP facebook_analytics_disk_usage_percent Disk usage percentage",
        f"# TYPE facebook_analytics_disk_usage_percent gauge",
        f"facebook_analytics_disk_usage_percent {disk.percent}",
        f"",
        f"# HELP facebook_analytics_cpu_usage_percent CPU usage percentage",
        f"# TYPE facebook_analytics_cpu_usage_percent gauge",
        f"facebook_analytics_cpu_usage_percent {cpu_percent}",
        f"",
        f"# HELP facebook_analytics_uptime_seconds Application uptime in seconds",
        f"# TYPE facebook_analytics_uptime_seconds counter",
        f"facebook_analytics_uptime_seconds {time.time()}",
    ]
    
    return "\n".join(metrics)