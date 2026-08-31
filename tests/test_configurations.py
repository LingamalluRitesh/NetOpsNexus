"""
Unit tests for Configuration Backup, Staged Deployment, and Atomic Rollback.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.devices.models import Device, DeviceType, DeviceStatus
from backend.app.devices.schemas import DeviceCreate
from backend.app.devices.service import DeviceService
from backend.app.configurations.models import ConfigTemplate, ConfigDeployment, BackupType, DeploymentStatus
from backend.app.configurations.schemas import ConfigTemplateCreate, ConfigDeploymentCreate, RollbackRequest
from backend.app.configurations.service import ConfigService
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
async def test_config_backup_and_history(test_db: AsyncSession):
    device = await DeviceService.create_device(
        test_db,
        DeviceCreate(
            hostname="RTR-CORE-01",
            management_ip="10.100.0.1",
            device_type=DeviceType.CORE_ROUTER,
            vendor="Cisco Systems",
            model="Catalyst 8500",
            os_type="cisco_ios",
            os_version="17.9",
        )
    )

    # Take backup 1
    b1 = await ConfigService.create_device_backup(test_db, device.id, comment="Initial baseline")
    assert b1.version_number == 1
    assert "hostname RTR-CORE-01" in b1.config_text

    # Take backup 2
    b2 = await ConfigService.create_device_backup(test_db, device.id, comment="Second snapshot")
    assert b2.version_number == 2

    history = await ConfigService.get_device_backup_history(test_db, device.id)
    assert len(history) == 2


@pytest.mark.asyncio
async def test_deployment_and_rollback(test_db: AsyncSession):
    device = await DeviceService.create_device(
        test_db,
        DeviceCreate(
            hostname="RTR-CORE-01",
            management_ip="10.100.0.1",
            device_type=DeviceType.CORE_ROUTER,
            vendor="Cisco Systems",
            model="Catalyst 8500",
            os_type="cisco_ios",
            os_version="17.9",
        )
    )

    # Baseline snapshot
    b_base = await ConfigService.create_device_backup(test_db, device.id, comment="Baseline")

    # Template
    template = await ConfigService.create_template(
        test_db,
        ConfigTemplateCreate(
            name="Interface Config",
            vendor="Cisco",
            os_type="cisco_ios",
            template_text="hostname {{ hostname }}\ninterface {{ int_name }}\n description {{ desc }}\n no shutdown\n",
        )
    )

    # Deploy without approval gate (direct execution)
    deploy_data = ConfigDeploymentCreate(
        title="Update Uplink Interface",
        target_device_ids=[device.id],
        template_id=template.id,
        template_vars={"hostname": "RTR-CORE-01", "int_name": "HundredGigE1/0/1", "desc": "Production Uplink"},
        approval_required=False,
    )
    deployment = await ConfigService.create_deployment(test_db, deploy_data)
    assert deployment.status == DeploymentStatus.VERIFIED
    assert len(deployment.logs) > 0

    # Execute Rollback
    rollback_req = RollbackRequest(device_id=device.id, target_version_id=b_base.id, comment="Revert update")
    restored = await ConfigService.rollback_device(test_db, rollback_req)
    assert restored.backup_type == BackupType.ROLLBACK_RESTORE
