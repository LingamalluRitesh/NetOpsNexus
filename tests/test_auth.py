"""
Unit tests for authentication, cryptographic hashing, and JWT token issuance.
"""

import pytest
import pytest_asyncio
from datetime import timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.auth.models import User, RefreshToken
from backend.app.auth.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from backend.app.auth.service import AuthService
from backend.app.auth.schemas import UserCreate
from backend.app.rbac.service import RBACService


@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await RBACService.initialize_roles_and_permissions(session)
        yield session

    await engine.dispose()


def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_generation():
    data = {"sub": "1", "username": "admin", "roles": ["super_admin"]}
    token = create_access_token(data, expires_delta=timedelta(minutes=15))
    assert isinstance(token, str)
    decoded = decode_token(token)
    assert decoded["sub"] == "1"
    assert decoded["username"] == "admin"
    assert decoded["type"] == "access"


@pytest.mark.asyncio
async def test_user_creation_and_authentication(test_db: AsyncSession):
    user_data = UserCreate(
        username="netadmin_test",
        email="netadmin@example.com",
        password="ValidPassword2026!",
        full_name="Network Admin Tester",
        roles=["network_admin"]
    )
    user = await AuthService.create_user(test_db, user_data)
    assert user.id is not None
    assert user.username == "netadmin_test"

    # Authenticate
    auth_user = await AuthService.authenticate_user(test_db, "netadmin_test", "ValidPassword2026!")
    assert auth_user is not None
    assert auth_user.id == user.id

    # Wrong password
    bad_auth = await AuthService.authenticate_user(test_db, "netadmin_test", "InvalidPassword")
    assert bad_auth is None

    # Tokens creation
    tokens = await AuthService.create_user_tokens(test_db, user)
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert tokens.token_type == "bearer"
