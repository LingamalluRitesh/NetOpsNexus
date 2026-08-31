"""
Unit tests for Telemetry Collection, Time-series metrics, and Monitoring Overview.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.devices.models import Device, DeviceType, DeviceStatus
from backend.app.devices.schemas import DeviceCreate
from backend.app.devices.service import DeviceService
from backend.app.monitoring.collector import TelemetryCollector
from backend.app.monitoring.service import MonitoringService
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
async def test_telemetry_collector_and_overview(test_db: AsyncSession):
    # Create test device
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

    # Run collection
    await TelemetryCollector.collect_single_device(test_db, device)

    # Query overview
    overview = await MonitoringService.get_overview(test_db)
    assert overview.total_devices_monitored >= 1
    assert overview.devices_online >= 1
    assert overview.average_network_cpu >= 0.0

    # Query device history
    history = await MonitoringService.get_device_history(test_db, device.id, hours=1)
    assert history.device_id == device.id
    assert len(history.cpu_series) > 0
    assert history.avg_cpu >= 0.0
