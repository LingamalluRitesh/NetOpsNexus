"""
Pydantic schemas for authentication requests, responses, and token envelopes.
"""

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: str
    username: str
    roles: List[str] = []
    permissions: List[str] = []
    exp: int


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    roles: List[str] = ["read_only"]


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    roles: Optional[List[str]] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    roles: List[str]
    permissions: List[str]
    last_login: Optional[datetime] = None
    created_at: datetime
