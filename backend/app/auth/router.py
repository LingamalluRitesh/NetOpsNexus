"""
Authentication API endpoints: login, token refresh, current user profile, password reset.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.auth.models import User
from backend.app.auth.schemas import LoginRequest, Token, RefreshTokenRequest, UserResponse, PasswordChangeRequest
from backend.app.auth.service import AuthService
from backend.app.auth.security import verify_password, get_password_hash
from backend.app.rbac.service import RBACService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Authenticate user with username and password, returning JWT access & refresh tokens."""
    user = await AuthService.authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await AuthService.create_user_tokens(db, user)


@router.post("/refresh", response_model=Token)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Issue a new access token using a valid refresh token."""
    return await AuthService.refresh_access_token(db, data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Any:
    """Get authenticated user profile, roles, and granular permissions."""
    roles = await RBACService.get_user_roles(db, current_user.id)
    perms = await RBACService.get_user_permissions(db, current_user.id)
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        roles=roles,
        permissions=list(perms),
        last_login=current_user.last_login,
        created_at=current_user.created_at,
    )


@router.post("/change-password")
async def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Change password for authenticated user."""
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password incorrect")
    
    current_user.hashed_password = get_password_hash(data.new_password)
    await db.commit()
    return {"message": "Password successfully updated"}
