from typing import List, Optional
from pydantic import BaseModel, EmailStr, constr

class LoginRequest(BaseModel):
    username: constr(min_length=3, max_length=80)
    password: constr(min_length=6)

class RegisterRequest(BaseModel):
    username: constr(min_length=3, max_length=80)
    email: EmailStr
    password: constr(min_length=6)
    first_name: Optional[constr(max_length=100)] = None
    last_name: Optional[constr(max_length=100)] = None
    roles: Optional[List[str]] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    status: str
    roles: List[str]

    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordUpdateRequest(BaseModel):
    current_password: constr(min_length=6)
    new_password: constr(min_length=6)

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    permissions: List[str]

    class Config:
        from_attributes = True

class PermissionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True 