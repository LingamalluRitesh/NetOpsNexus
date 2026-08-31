"""
Unit tests for RBAC permission resolution, role initialization, and role creation.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.rbac.models import Role, PermissionModel
from backend.app.rbac.permissions import Permission, RoleName
from backend.app.rbac.service import RBACService
from backend.app.rbac.schemas import RoleCreate
from backend.app.auth.service import AuthService
from backend.app.auth.schemas import UserCreate


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


@pytest.mark.asyncio
async def test_rbac_initialization(test_db: AsyncSession):
    roles = await RBACService.list_roles(test_db)
    role_names = [r.name for r in roles]
    assert RoleName.SUPER_ADMIN.value in role_names
    assert RoleName.NETWORK_ADMIN.value in role_names
    assert RoleName.NOC_ENGINEER.value in role_names
    assert RoleName.READ_ONLY.value in role_names


@pytest.mark.asyncio
async def test_user_permissions_resolution(test_db: AsyncSession):
    user_data = UserCreate(
        username="noc_user",
        email="noc@example.com",
        password="NocPassword2026!",
        full_name="NOC Tech",
        roles=["noc_engineer"]
    )
    user = await AuthService.create_user(test_db, user_data)
    perms = await RBACService.get_user_permissions(test_db, user.id)
    
    assert Permission.MONITORING_READ.value in perms
    assert Permission.INCIDENTS_CREATE.value in perms
    assert Permission.DEVICES_DELETE.value not in perms  # NOC engineer cannot delete devices


@pytest.mark.asyncio
async def test_custom_role_creation(test_db: AsyncSession):
    role_create = RoleCreate(
        name="custom_diagnostics_role",
        description="Role for diagnostic testing only",
        permissions=[Permission.DIAGNOSTICS_RUN.value, Permission.DEVICES_READ.value]
    )
    role = await RBACService.create_role(test_db, role_create)
    assert role.id is not None
    assert role.name == "custom_diagnostics_role"
