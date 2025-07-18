from functools import wraps
from typing import List, Optional
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_403_FORBIDDEN
from app.services.auth_service import AuthService
from app.database import get_db

security = HTTPBearer()

def require_auth(roles: Optional[List[str]] = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, token: HTTPAuthorizationCredentials = Security(security), **kwargs):
            db = next(get_db())
            try:
                # Verify token and get user
                user = AuthService.get_current_user(db, token.credentials)
                
                # Check if user is active
                if user.status != 'active':
                    raise HTTPException(
                        status_code=HTTP_403_FORBIDDEN,
                        detail="Inactive user account"
                    )
                
                # Check roles if specified
                if roles:
                    user_roles = [role.name for role in user.user_roles_rel]
                    if not any(role in user_roles for role in roles):
                        raise HTTPException(
                            status_code=HTTP_403_FORBIDDEN,
                            detail="Insufficient permissions"
                        )
                
                # Add user to kwargs
                kwargs['current_user'] = user
                return await func(*args, **kwargs)
                
            except ValueError as e:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail=str(e)
                )
            finally:
                db.close()
                
        return wrapper
    return decorator

def require_roles(roles: List[str]):
    """Decorator for role-based access control"""
    return require_auth(roles=roles)

def is_admin(func):
    """Decorator for admin-only routes"""
    return require_auth(roles=['admin'])(func)

def is_course_manager(func):
    """Decorator for course manager routes"""
    return require_auth(roles=['course_manager', 'admin'])(func)

def is_trainer(func):
    """Decorator for trainer routes"""
    return require_auth(roles=['trainer', 'admin'])(func)

def is_sales(func):
    """Decorator for sales routes"""
    return require_auth(roles=['sales', 'admin'])(func) 