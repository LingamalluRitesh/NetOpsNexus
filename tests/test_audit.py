"""
Unit tests for Immutable Operations and Security Audit Trail.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.audit.models import AuditLog
from backend.app.audit.service import AuditService
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


@pytest.mark.asyncio
async def test_audit_logging_and_query(test_db: AsyncSession):
    entry = await AuditService.log_action(
        test_db,
        username="admin",
        action="config_deploy",
        resource_type="config",
        resource_id="12",
        details={"deployment_title": "Interface Upgrade", "targets": [1, 2, 3]},
        ip_address="192.168.1.100",
    )
    assert entry.id is not None
    assert entry.action == "config_deploy"

    logs = await AuditService.list_logs(test_db, resource_type="config")
    assert len(logs) >= 1
    assert logs[0].username == "admin"
    assert logs[0].details["deployment_title"] == "Interface Upgrade"
