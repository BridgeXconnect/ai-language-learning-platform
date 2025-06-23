from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    PasswordResetRequest,
    PasswordUpdateRequest
)

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = UserService.create_user(
            db=db,
            username=request.username,
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            roles=request.roles
        )
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if user.status != 'active':
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="User account is not active"
        )
    
    return AuthService.create_tokens_for_user(user)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = AuthService.get_current_user(db, token.credentials)
        return AuthService.create_tokens_for_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.post("/reset-password")
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    user = UserService.get_user_by_email(db, request.email)
    if not user:
        # Return success even if user doesn't exist for security
        return {"message": "If the email exists, a reset link has been sent"}
    
    # TODO: Implement email service to send reset link
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/update-password")
async def update_password(
    request: PasswordUpdateRequest,
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user = AuthService.get_current_user(db, token.credentials)
        
        # Verify current password
        if not AuthService.verify_password(request.current_password, user.password_hash):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Update password
        UserService.update_user(
            db,
            user.id,
            {"password": request.new_password}
        )
        
        return {"message": "Password updated successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=str(e)
        ) 