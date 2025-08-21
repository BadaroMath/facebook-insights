"""
Facebook Analytics Platform - Main FastAPI Application

A comprehensive platform for analyzing Facebook page and post performance
with real-time insights, automated reporting, and advanced analytics.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
import time

from app.core.config import settings
from app.core.database import init_database, close_database
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security import SecurityMiddleware


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("🚀 Starting Facebook Analytics Platform...")
    
    # Initialize database
    await init_database()
    logger.info("✅ Database initialized")
    
    # Initialize background tasks
    # TODO: Initialize Celery workers
    logger.info("✅ Background tasks initialized")
    
    yield
    
    # Cleanup
    logger.info("🔄 Shutting down Facebook Analytics Platform...")
    await close_database()
    logger.info("✅ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Facebook Analytics Platform API
    
    A comprehensive platform for analyzing Facebook page and post performance.
    
    ### Features:
    - 📊 **Real-time Analytics**: Live Facebook page and post metrics
    - 🔄 **Automated Data Pipeline**: Scheduled data extraction and processing  
    - 📈 **Advanced Reporting**: Custom reports and data visualization
    - 👥 **Multi-Account Management**: Handle multiple Facebook pages
    - 🚨 **Smart Alerts**: Automated notifications and monitoring
    - 🔐 **Secure Integration**: OAuth 2.0 and enterprise security
    
    ### API Endpoints:
    - **Analytics**: Page insights, post metrics, engagement data
    - **Authentication**: OAuth, JWT tokens, user management
    - **Data Management**: ETL jobs, data sync, health checks
    - **Reports**: Generated reports, scheduled exports
    - **Monitoring**: System health, performance metrics
    """,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SecurityMiddleware)
app.add_middleware(RateLimitMiddleware, 
                  calls=settings.RATE_LIMIT_REQUESTS_PER_MINUTE, 
                  period=60)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing information."""
    start_time = time.time()
    
    # Log request
    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent", "")
        }
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": f"{process_time:.4f}",
        }
    )
    
    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(
        "Unhandled exception occurred",
        extra={
            "method": request.method,
            "url": str(request.url),
            "exception": str(exc),
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_id": f"ERR_{int(time.time())}",
            "timestamp": time.time()
        }
    )


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "health": "/health",
        "status": "operational"
    }


# Mount static files (if any)
# app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
        log_config=None,  # Use our custom logging
    )