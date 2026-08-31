"""
Service layer for authentication, token generation, user creation, and profile retrieval.
"""

from typing import Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.auth.models import User, RefreshToken
from backend.app.auth.schemas import UserCreate, UserUpdate, Token
from backend.app.auth.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from backend.app.rbac.service import RBACService
from backend.app.config import settings


class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Verify username and password against database."""
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")
        
        # Update last login timestamp
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
        return user

    @staticmethod
    async def create_user_tokens(db: AsyncSession, user: User) -> Token:
        """Create access and refresh token pair and persist refresh token in DB."""
        roles = await RBACService.get_user_roles(db, user.id)
        perms = await RBACService.get_user_permissions(db, user.id)

        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "roles": roles,
            "permissions": list(perms),
        }

        access_token = create_access_token(token_data)
        refresh_token_str = create_refresh_token(token_data)

        # Persist refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        rf_model = RefreshToken(
            user_id=user.id,
            token=refresh_token_str,
            expires_at=expires_at,
            is_revoked=False
        )
        db.add(rf_model)
        await db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token_str: str) -> Token:
        """Validate refresh token and issue a new access token."""
        try:
            payload = decode_token(refresh_token_str)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
            user_id = int(payload.get("sub"))
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token == refresh_token_str,
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            )
        )
        db_rf = result.scalar_one_or_none()
        if not db_rf or db_rf.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Revoked or expired refresh token")

        result_user = await db.execute(select(User).where(User.id == user_id))
        user = result_user.scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

        # Invalidate old refresh token and issue new token pair
        db_rf.is_revoked = True
        return await AuthService.create_user_tokens(db, user)

    @staticmethod
    async def create_user(db: AsyncSession, data: UserCreate) -> User:
        """Register a new user and assign roles."""
        # Check uniqueness
        res = await db.execute(select(User).where((User.username == data.username) | (User.email == data.email)))
        if res.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        await db.flush()

        # Assign roles
        await RBACService.assign_user_roles(db, user.id, data.roles)
        await db.commit()
        return user
