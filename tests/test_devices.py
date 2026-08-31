"""
Unit tests for Device inventory, site hierarchy, and device synchronization.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.devices.models import Device, Site, DeviceType, DeviceStatus
from backend.app.devices.schemas import DeviceCreate, SiteCreate, DeviceUpdate
from backend.app.devices.service import DeviceService
from backend.app.devices.repository import SiteRepository, DeviceRepository
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
async def test_site_creation(test_db: AsyncSession):
    site_data = SiteCreate(
        name="San Jose Campus",
        code="SJC-01",
        city="San Jose",
        country="USA",
        latitude=37.3382,
        longitude=-121.8863
    )
    site = await SiteRepository.create(test_db, site_data)
    assert site.id is not None
    assert site.name == "San Jose Campus"


@pytest.mark.asyncio
async def test_device_creation_and_sync(test_db: AsyncSession):
    # Create Site
    site = await SiteRepository.create(
        test_db,
        SiteCreate(name="HQ Data Center", code="HQ-DC", city="New York", country="USA")
    )

    dev_data = DeviceCreate(
        hostname="RTR-CORE-01",
        management_ip="10.100.0.1",
        device_type=DeviceType.CORE_ROUTER,
        vendor="Cisco Systems",
        model="Catalyst 8500",
        os_type="cisco_ios",
        os_version="17.9.4",
        site_id=site.id,
        status=DeviceStatus.ONLINE
    )
    device = await DeviceService.create_device(test_db, dev_data)
    assert device.id is not None
    assert device.hostname == "RTR-CORE-01"
    # Verify interfaces and routes were auto-synchronized from adapter
    assert len(device.interfaces) > 0
    assert len(device.routes) > 0
    assert device.cpu_utilization > 0.0


@pytest.mark.asyncio
async def test_device_update_and_delete(test_db: AsyncSession):
    dev_data = DeviceCreate(
        hostname="SW-TEMP-01",
        management_ip="10.100.0.99",
        device_type=DeviceType.ACCESS_SWITCH,
        vendor="Cisco",
        model="Catalyst 9300",
        os_type="cisco_ios",
        os_version="17.9",
        status=DeviceStatus.ONLINE
    )
    device = await DeviceService.create_device(test_db, dev_data)
    
    # Update
    updated = await DeviceService.update_device(
        test_db, device.id, DeviceUpdate(status=DeviceStatus.MAINTENANCE)
    )
    assert updated.status == DeviceStatus.MAINTENANCE

    # Delete
    await DeviceService.delete_device(test_db, device.id)
    with pytest.raises(Exception):
        await DeviceService.get_device(test_db, device.id)
