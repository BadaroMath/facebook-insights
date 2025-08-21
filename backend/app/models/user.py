"""
User model for authentication and profile management.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import EmailStr, Field
from beanie import Document, Indexed
from pymongo import IndexModel


class User(Document):
    """User document model."""
    
    # Basic information
    email: Indexed(EmailStr, unique=True)
    full_name: str
    is_active: bool = True
    is_superuser: bool = False
    
    # Password (hashed)
    hashed_password: str
    
    # Facebook integration
    facebook_user_id: Optional[Indexed(str, unique=True)] = None
    facebook_access_token: Optional[str] = None
    facebook_token_expires_at: Optional[datetime] = None
    
    # Profile information
    avatar_url: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    
    # Account settings
    email_notifications: bool = True
    marketing_emails: bool = False
    data_retention_days: int = 365
    
    # Usage statistics
    last_login_at: Optional[datetime] = None
    pages_connected: int = 0
    reports_generated: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = [
            IndexModel("email", unique=True),
            IndexModel("facebook_user_id", unique=True, sparse=True),
            IndexModel("created_at"),
            IndexModel("is_active"),
        ]
    
    def __str__(self):
        return f"User(email={self.email})"
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def is_facebook_connected(self) -> bool:
        """Check if user has connected Facebook account."""
        return (
            self.facebook_user_id is not None and
            self.facebook_access_token is not None and
            self.facebook_token_expires_at is not None and
            self.facebook_token_expires_at > datetime.utcnow()
        )
    
    def increment_pages_connected(self):
        """Increment connected pages counter."""
        self.pages_connected += 1
        self.updated_at = datetime.utcnow()
    
    def increment_reports_generated(self):
        """Increment generated reports counter."""
        self.reports_generated += 1
        self.updated_at = datetime.utcnow()


class UserCreate(Document):
    """Schema for creating new users."""
    email: EmailStr
    full_name: str
    password: str


class UserUpdate(Document):
    """Schema for updating user information."""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    email_notifications: Optional[bool] = None
    marketing_emails: Optional[bool] = None
    data_retention_days: Optional[int] = None


class UserResponse(Document):
    """Schema for user responses (without sensitive data)."""
    id: str
    email: EmailStr
    full_name: str
    is_active: bool
    avatar_url: Optional[str] = None
    timezone: str
    language: str
    email_notifications: bool
    marketing_emails: bool
    last_login_at: Optional[datetime] = None
    pages_connected: int
    reports_generated: int
    created_at: datetime
    updated_at: datetime
    is_facebook_connected: bool


class FacebookUserInfo(Document):
    """Facebook user information from Graph API."""
    facebook_user_id: str
    name: str
    email: Optional[str] = None
    picture_url: Optional[str] = None
    access_token: str
    expires_at: datetime