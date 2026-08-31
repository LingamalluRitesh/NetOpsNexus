"""
Unit tests for network interface lifecycle and traffic counters.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.devices.models import Device, NetworkInterface, DeviceType, DeviceStatus, InterfaceOperStatus
from backend.app.devices.schemas import DeviceCreate
from backend.app.devices.service import DeviceService
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
async def test_interface_traffic_and_status(test_db: AsyncSession):
    dev_data = DeviceCreate(
        hostname="SW-SPINE-01",
        management_ip="10.100.0.11",
        device_type=DeviceType.SPINE_SWITCH,
        vendor="Arista Networks",
        model="DCS-7050X3",
        os_type="arista_eos",
        os_version="4.30",
    )
    device = await DeviceService.create_device(test_db, dev_data)
    assert len(device.interfaces) >= 4

    # Check interface attributes
    uplink = next((i for i in device.interfaces if "HundredGigE" in i.name), None)
    assert uplink is not None
    assert uplink.speed_mbps == 100000
    assert uplink.oper_status == InterfaceOperStatus.UP
    assert uplink.rx_bps >= 0.0
    assert uplink.tx_bps >= 0.0
