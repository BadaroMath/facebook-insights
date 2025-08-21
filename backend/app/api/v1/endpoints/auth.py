"""
Authentication endpoints for user login, registration, and Facebook OAuth.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.models.user import User, UserCreate, UserResponse, FacebookUserInfo
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class FacebookLoginRequest(BaseModel):
    access_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = await User.get(user_id)
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/register", response_model=TokenResponse, summary="Register new user")
async def register(user_data: UserCreate) -> TokenResponse:
    """Register a new user account."""
    
    # Check if user already exists
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    await user.save()
    logger.info(f"New user registered: {user.email}")
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Convert user to response model
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
        timezone=user.timezone,
        language=user.language,
        email_notifications=user.email_notifications,
        marketing_emails=user.marketing_emails,
        last_login_at=user.last_login_at,
        pages_connected=user.pages_connected,
        reports_generated=user.reports_generated,
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_facebook_connected=user.is_facebook_connected()
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )


@router.post("/login", response_model=TokenResponse, summary="User login")
async def login(login_data: LoginRequest) -> TokenResponse:
    """Authenticate user and return tokens."""
    
    # Find user
    user = await User.find_one(User.email == login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.update_last_login()
    await user.save()
    
    logger.info(f"User logged in: {user.email}")
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Convert user to response model
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
        timezone=user.timezone,
        language=user.language,
        email_notifications=user.email_notifications,
        marketing_emails=user.marketing_emails,
        last_login_at=user.last_login_at,
        pages_connected=user.pages_connected,
        reports_generated=user.reports_generated,
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_facebook_connected=user.is_facebook_connected()
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )


@router.post("/facebook", response_model=TokenResponse, summary="Facebook OAuth login")
async def facebook_login(facebook_data: FacebookLoginRequest) -> TokenResponse:
    """Login or register user using Facebook OAuth."""
    
    # Verify Facebook token and get user info
    facebook_user = await get_facebook_user_info(facebook_data.access_token)
    
    if not facebook_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Facebook access token"
        )
    
    # Find existing user by Facebook ID or email
    user = await User.find_one(User.facebook_user_id == facebook_user.facebook_user_id)
    
    if not user and facebook_user.email:
        user = await User.find_one(User.email == facebook_user.email)
    
    if user:
        # Update existing user's Facebook info
        user.facebook_user_id = facebook_user.facebook_user_id
        user.facebook_access_token = facebook_user.access_token
        user.facebook_token_expires_at = facebook_user.expires_at
        
        if not user.avatar_url and facebook_user.picture_url:
            user.avatar_url = facebook_user.picture_url
        
        user.update_last_login()
        await user.save()
        
    else:
        # Create new user
        user = User(
            email=facebook_user.email,
            full_name=facebook_user.name,
            hashed_password=get_password_hash("facebook_oauth_user"),  # Dummy password
            facebook_user_id=facebook_user.facebook_user_id,
            facebook_access_token=facebook_user.access_token,
            facebook_token_expires_at=facebook_user.expires_at,
            avatar_url=facebook_user.picture_url
        )
        await user.save()
        logger.info(f"New Facebook user registered: {user.email}")
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Convert user to response model
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
        timezone=user.timezone,
        language=user.language,
        email_notifications=user.email_notifications,
        marketing_emails=user.marketing_emails,
        last_login_at=user.last_login_at,
        pages_connected=user.pages_connected,
        reports_generated=user.reports_generated,
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_facebook_connected=user.is_facebook_connected()
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh_token(refresh_data: RefreshTokenRequest) -> TokenResponse:
    """Refresh access token using refresh token."""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token"
    )
    
    try:
        payload = jwt.decode(
            refresh_data.refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = await User.get(user_id)
    if user is None or not user.is_active:
        raise credentials_exception
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Convert user to response model
    user_response = UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
        timezone=user.timezone,
        language=user.language,
        email_notifications=user.email_notifications,
        marketing_emails=user.marketing_emails,
        last_login_at=user.last_login_at,
        pages_connected=user.pages_connected,
        reports_generated=user.reports_generated,
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_facebook_connected=user.is_facebook_connected()
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Get current user information."""
    
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


@router.post("/logout", summary="User logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (in a real implementation, you'd blacklist the token)."""
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}


async def get_facebook_user_info(access_token: str) -> Optional[FacebookUserInfo]:
    """Get user information from Facebook Graph API."""
    try:
        async with httpx.AsyncClient() as client:
            # Get user info
            response = await client.get(
                f"https://graph.facebook.com/me",
                params={
                    "access_token": access_token,
                    "fields": "id,name,email,picture"
                }
            )
            
            if response.status_code != 200:
                return None
            
            user_data = response.json()
            
            # Get token info for expiration
            token_response = await client.get(
                f"https://graph.facebook.com/oauth/access_token_info",
                params={"access_token": access_token}
            )
            
            expires_in = 3600  # Default 1 hour
            if token_response.status_code == 200:
                token_info = token_response.json()
                expires_in = token_info.get("expires_in", 3600)
            
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            return FacebookUserInfo(
                facebook_user_id=user_data["id"],
                name=user_data["name"],
                email=user_data.get("email"),
                picture_url=user_data.get("picture", {}).get("data", {}).get("url"),
                access_token=access_token,
                expires_at=expires_at
            )
            
    except Exception as e:
        logger.error(f"Error getting Facebook user info: {e}")
        return None