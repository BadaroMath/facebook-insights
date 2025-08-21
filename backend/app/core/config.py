"""
Application configuration management using Pydantic settings.
Handles environment variables, validation, and default values.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import BaseSettings, validator
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    APP_NAME: str = "Facebook Analytics Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    # API
    API_V1_PREFIX: str = "/api"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database
    MONGO_URL: str = "mongodb://localhost:27017/facebook_analytics"
    MONGO_DB_NAME: str = "facebook_analytics"
    
    # Facebook API
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_REDIRECT_URI: str = "http://localhost:3000/auth/facebook/callback"
    FACEBOOK_API_VERSION: str = "v18.0"
    FACEBOOK_BASE_URL: str = "https://graph.facebook.com"
    
    # Google Cloud Platform
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    BIGQUERY_DATASET_ID: str = "facebook_analytics"
    SECRET_MANAGER_PROJECT_ID: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    JWT_SECRET_KEY: str = "dev-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    PROMETHEUS_PORT: int = 9090
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Data Processing
    MAX_POSTS_PER_PAGE: int = 100
    DATA_RETENTION_DAYS: int = 365
    SYNC_INTERVAL_MINUTES: int = 60
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        """Validate environment setting."""
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Environment must be one of: {valid_envs}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level setting."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()


# Helper functions for environment-specific settings
def is_development() -> bool:
    """Check if running in development environment."""
    return settings.ENVIRONMENT == "development"


def is_production() -> bool:
    """Check if running in production environment."""
    return settings.ENVIRONMENT == "production"


def is_testing() -> bool:
    """Check if running in testing environment."""
    return settings.ENVIRONMENT == "testing"


def get_database_url() -> str:
    """Get the complete database URL."""
    return settings.MONGO_URL


def get_facebook_graph_url(endpoint: str = "") -> str:
    """Get Facebook Graph API URL for given endpoint."""
    base_url = f"{settings.FACEBOOK_BASE_URL}/{settings.FACEBOOK_API_VERSION}"
    return f"{base_url}/{endpoint}" if endpoint else base_url


def get_bigquery_table_name(table_type: str, username: str) -> str:
    """Generate BigQuery table name for given type and username."""
    return f"facebook_{table_type}_{username}"