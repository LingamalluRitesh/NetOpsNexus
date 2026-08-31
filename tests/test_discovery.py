"""
Unit tests for Network Discovery scanner, job pipeline, and inventory import.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from backend.app.database import Base
from backend.app.discovery.models import DiscoveryJob, DiscoveredDevice, JobStatus, ScanType
from backend.app.discovery.schemas import DiscoveryScanConfig, ImportDiscoveredRequest
from backend.app.discovery.service import DiscoveryService
from backend.app.discovery.engine import DiscoveryEngine
from backend.app.devices.repository import SiteRepository
from backend.app.devices.schemas import SiteCreate
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
async def test_discovery_job_creation_and_pipeline(test_db: AsyncSession):
    config = DiscoveryScanConfig(
        name="Data Center Core Sweep",
        target_cidr="10.100.0.0/28",
        scan_type=ScanType.FULL_DISCOVERY,
        snmp_community="public",
    )
    job = DiscoveryJob(
        name=config.name,
        target_cidr=config.target_cidr,
        scan_type=config.scan_type,
        status=JobStatus.QUEUED,
        snmp_community=config.snmp_community,
    )
    test_db.add(job)
    await test_db.commit()
    await test_db.refresh(job)

    # Run pipeline synchronously for test
    await DiscoveryEngine.run_discovery_pipeline(test_db, job)
    await test_db.refresh(job, ["discovered_devices"])

    assert job.status == JobStatus.COMPLETED
    assert job.progress_percent == 100
    assert job.discovered_count > 0
    assert len(job.discovered_devices) > 0

    first_dev = job.discovered_devices[0]
    assert first_dev.ip_address is not None
    assert first_dev.hostname is not None


@pytest.mark.asyncio
async def test_import_discovered_devices(test_db: AsyncSession):
    # Create Site
    site = await SiteRepository.create(
        test_db, SiteCreate(name="HQ DC Site", code="HQ-DC-1", city="NYC", country="USA")
    )

    job = DiscoveryJob(
        name="Campus Discovery",
        target_cidr="10.200.0.0/28",
        status=JobStatus.QUEUED,
    )
    test_db.add(job)
    await test_db.commit()
    await test_db.refresh(job)

    await DiscoveryEngine.run_discovery_pipeline(test_db, job)
    await test_db.refresh(job, ["discovered_devices"])
    assert len(job.discovered_devices) > 0

    dev_ids = [d.id for d in job.discovered_devices[:2]]
    import_req = ImportDiscoveredRequest(device_ids=dev_ids, target_site_id=site.id)
    imported = await DiscoveryService.import_devices(test_db, import_req)
    
    assert len(imported) == len(dev_ids)
    assert imported[0].id is not None
    assert imported[0].site_id == site.id
