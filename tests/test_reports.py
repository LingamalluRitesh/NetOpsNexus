"""
Unit tests for PDF and CSV Report Generators.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.devices.models import Device, DeviceType, DeviceStatus
from backend.app.devices.schemas import DeviceCreate
from backend.app.devices.service import DeviceService
from backend.app.reports.pdf_generator import PdfReportGenerator
from backend.app.reports.service import ReportsService
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


def test_pdf_report_generator():
    data = {
        "total_devices": 24,
        "health_score": 96.5,
        "security_score": 92.0,
        "mttr_min": 12.0,
        "active_p1_p2": 0,
    }
    pdf_bytes = PdfReportGenerator.generate_executive_summary_pdf(data)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_devices_csv_export(test_db: AsyncSession):
    await DeviceService.create_device(
        test_db,
        DeviceCreate(
            hostname="RTR-CORE-01",
            management_ip="10.100.0.1",
            device_type=DeviceType.CORE_ROUTER,
            vendor="Cisco",
            model="Catalyst 8500",
            os_type="cisco_ios",
            os_version="17.9",
        )
    )

    csv_data = await ReportsService.export_devices_csv(test_db)
    assert "Hostname,Management IP,Device Type" in csv_data
    assert "RTR-CORE-01,10.100.0.1,core_router" in csv_data
