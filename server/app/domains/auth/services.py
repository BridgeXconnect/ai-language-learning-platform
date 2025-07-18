"""
Auth Domain - Services
Consolidated from: auth_service.py, user_service.py
"""

from app.core.config import settings
from app.core.database import get_db
from app.domains.auth.models import User
from app.domains.auth.models import User, Role, Permission
from app.domains.auth.services import AuthService
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from typing import Optional, Dict
import jwt

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Dict:
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except InvalidTokenError:
            raise ValueError("Invalid token")

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def create_tokens_for_user(user: User) -> Dict[str, str]:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        refresh_token = AuthService.create_refresh_token(
            data={"sub": user.username}
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        payload = AuthService.decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise ValueError("Invalid token payload")
        
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise ValueError("User not found")
            
        return user

# FastAPI dependency function
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency to get current authenticated user."""
    try:
        user = AuthService.get_current_user(db, credentials.credentials)
        if user.status != 'active':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account"
            )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) 
class UserService:
    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        roles: Optional[List[str]] = None
    ) -> User:
        # Hash password
        hashed_password = AuthService.get_password_hash(password)
        
        # Create user instance
        user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Add roles if provided
        if roles:
            role_instances = db.query(Role).filter(Role.name.in_(roles)).all()
            user.user_roles_rel = role_instances
        
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValueError("Username or email already exists")

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None
    ) -> List[User]:
        query = db.query(User)
        if role:
            query = query.join(User.user_roles_rel).filter(Role.name == role)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        update_data: Dict
    ) -> Optional[User]:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
            
        # Update user fields
        for key, value in update_data.items():
            if key == 'password':
                user.password_hash = AuthService.get_password_hash(value)
            elif key == 'roles':
                role_instances = db.query(Role).filter(Role.name.in_(value)).all()
                user.user_roles_rel = role_instances
            elif hasattr(user, key):
                setattr(user, key, value)
        
        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValueError("Update failed due to constraint violation")

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False
            
        try:
            db.delete(user)
            db.commit()
            return True
        except:
            db.rollback()
            return False

    @staticmethod
    def create_role(
        db: Session,
        name: str,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None
    ) -> Role:
        role = Role(name=name, description=description)
        
        if permissions:
            permission_instances = db.query(Permission).filter(
                Permission.name.in_(permissions)
            ).all()
            role.permissions = permission_instances
        
        try:
            db.add(role)
            db.commit()
            db.refresh(role)
            return role
        except IntegrityError:
            db.rollback()
            raise ValueError("Role name already exists")

    @staticmethod
    def get_role_by_name(db: Session, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def create_permission(
        db: Session,
        name: str,
        description: Optional[str] = None
    ) -> Permission:
        permission = Permission(name=name, description=description)
        
        try:
            db.add(permission)
            db.commit()
            db.refresh(permission)
            return permission
        except IntegrityError:
            db.rollback()
            raise ValueError("Permission name already exists") 
