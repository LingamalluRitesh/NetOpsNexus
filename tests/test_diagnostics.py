"""
Unit tests for Network Diagnostics Toolkit (Ping, Traceroute, DNS, Port Probes).
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.diagnostics.schemas import PingRequest, TracerouteRequest, DnsLookupRequest, PortProbeRequest
from backend.app.diagnostics.service import DiagnosticsService


@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_diagnostics_ping(test_db: AsyncSession):
    req = PingRequest(target="10.100.0.1", count=4)
    res = await DiagnosticsService.run_ping(test_db, req)
    assert res.target == "10.100.0.1"
    assert res.is_reachable is True
    assert res.packets_sent == 4
    assert res.avg_rtt_ms >= 0.0


@pytest.mark.asyncio
async def test_diagnostics_traceroute(test_db: AsyncSession):
    req = TracerouteRequest(target="8.8.8.8", max_hops=10)
    res = await DiagnosticsService.run_traceroute(test_db, req)
    assert res.total_hops > 0
    assert len(res.hops) > 0
    assert res.hops[0].hop_number == 1


@pytest.mark.asyncio
async def test_diagnostics_dns():
    req = DnsLookupRequest(query_name="google.com", record_type="A")
    res = await DiagnosticsService.run_dns_lookup(req)
    assert res.query_name == "google.com"
    assert len(res.answers) > 0


@pytest.mark.asyncio
async def test_diagnostics_port_probe():
    req = PortProbeRequest(target_ip="10.100.0.1", port=22)
    res = await DiagnosticsService.run_port_probe(req)
    assert res.target_ip == "10.100.0.1"
    assert res.port == 22
    assert res.is_open is True
    assert res.service_name == "SSH"
