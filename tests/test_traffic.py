"""
Unit tests for NetFlow / sFlow Ingestion and Top Talkers Aggregation.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.traffic.models import TrafficFlowRecord
from backend.app.traffic.schemas import FlowRecordCreate
from backend.app.traffic.flow_engine import TrafficFlowEngine
from backend.app.traffic.service import TrafficService
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


def test_top_talkers_aggregation():
    records = [
        TrafficFlowRecord(src_ip="10.100.1.10", dst_ip="1.1.1.1", src_port=5000, dst_port=53, protocol="UDP", bytes_count=1000000, packets_count=500, application_name="DNS"),
        TrafficFlowRecord(src_ip="10.100.1.10", dst_ip="142.250.190.46", src_port=5001, dst_port=443, protocol="TCP", bytes_count=9000000, packets_count=4500, application_name="HTTPS"),
        TrafficFlowRecord(src_ip="10.100.2.20", dst_ip="142.250.190.46", src_port=5002, dst_port=443, protocol="TCP", bytes_count=2000000, packets_count=1000, application_name="HTTPS"),
    ]

    res = TrafficFlowEngine.calculate_top_talkers(records)
    assert len(res.top_sources) >= 2
    assert res.top_sources[0].entity == "10.100.1.10"
    assert res.top_sources[0].bytes_total == 10000000
    assert res.top_applications[0].entity == "HTTPS"


@pytest.mark.asyncio
async def test_flow_ingestion_service(test_db: AsyncSession):
    flows = [
        FlowRecordCreate(src_ip="10.0.0.1", dst_ip="10.0.0.2", src_port=1024, dst_port=80, protocol="TCP", bytes_count=50000, packets_count=30, application_name="HTTP"),
        FlowRecordCreate(src_ip="10.0.0.3", dst_ip="10.0.0.4", src_port=1025, dst_port=443, protocol="TCP", bytes_count=150000, packets_count=90, application_name="HTTPS"),
    ]
    count = await TrafficService.ingest_flows(test_db, flows)
    assert count == 2

    talkers = await TrafficService.get_top_talkers(test_db, hours=1)
    assert len(talkers.top_sources) > 0
