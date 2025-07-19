"""
Authentication Routes for AI Language Learning Platform
Created by: James (BMAD Developer)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.services.authentication_service import (
    auth_service, 
    UserRegistration, 
    UserLogin, 
    TokenResponse, 
    UserResponse
)
from app.models.database_models import User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer()

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    return await auth_service.get_current_user(db, token)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistration,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    - **email**: User's email address (must be unique)
    - **username**: User's username (must be unique)
    - **password**: User's password (will be hashed)
    - **first_name**: User's first name (optional)
    - **last_name**: User's last name (optional)
    - **phone**: User's phone number (optional)
    """
    try:
        user = await auth_service.register_user(db, user_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access tokens
    
    - **email**: User's email address
    - **password**: User's password
    """
    try:
        tokens = await auth_service.login_user(db, credentials)
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    """
    try:
        tokens = await auth_service.refresh_token(db, refresh_token)
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile information
    
    Requires authentication
    """
    return UserResponse(**current_user.to_dict())

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    
    - **first_name**: User's first name (optional)
    - **last_name**: User's last name (optional)
    - **phone**: User's phone number (optional)
    
    Requires authentication
    """
    try:
        user = await auth_service.update_user_profile(db, str(current_user.id), update_data)
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user's password
    
    - **current_password**: Current password for verification
    - **new_password**: New password to set
    
    Requires authentication
    """
    try:
        success = await auth_service.change_password(
            db, 
            str(current_user.id), 
            current_password, 
            new_password
        )
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.post("/verify-email")
async def verify_email(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark user's email as verified
    
    Requires authentication
    """
    try:
        success = await auth_service.verify_email(db, str(current_user.id))
        return {"message": "Email verified successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )

@router.post("/logout")
async def logout():
    """
    Logout user (client-side token removal)
    
    Note: This is a client-side operation. The server doesn't maintain session state.
    Clients should remove the stored tokens.
    """
    return {"message": "Logged out successfully"}

# Health check endpoint
@router.get("/health")
async def auth_health_check():
    """Health check for authentication service"""
    return {
        "status": "healthy",
        "service": "authentication",
        "version": "2.0.0"
    } 