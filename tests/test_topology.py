"""
Unit tests for Topology Graph Engine, Dijkstra path tracing, SPOF detection, and blast radius analysis.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.devices.models import Device, DeviceType, DeviceStatus
from backend.app.devices.schemas import DeviceCreate
from backend.app.devices.service import DeviceService
from backend.app.topology.models import NetworkLink, LinkType, LinkStatus
from backend.app.topology.schemas import PathTraceRequest
from backend.app.topology.service import TopologyService
from backend.app.topology.graph_engine import TopologyGraphEngine
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
async def test_topology_graph_and_links(test_db: AsyncSession):
    # Create 3 tier topology: Core -> Spine -> Leaf
    d_core = await DeviceService.create_device(
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
    d_spine = await DeviceService.create_device(
        test_db,
        DeviceCreate(
            hostname="SW-SPINE-01",
            management_ip="10.100.0.11",
            device_type=DeviceType.SPINE_SWITCH,
            vendor="Arista",
            model="DCS-7050",
            os_type="arista_eos",
            os_version="4.30",
        )
    )
    d_leaf = await DeviceService.create_device(
        test_db,
        DeviceCreate(
            hostname="SW-LEAF-01",
            management_ip="10.100.0.21",
            device_type=DeviceType.LEAF_SWITCH,
            vendor="Arista",
            model="DCS-7050",
            os_type="arista_eos",
            os_version="4.30",
        )
    )

    # Fetch topology
    graph = await TopologyService.get_topology_graph(test_db)
    assert graph.total_nodes >= 3
    assert graph.total_edges >= 2


@pytest.mark.asyncio
async def test_path_tracing(test_db: AsyncSession):
    d_core = await DeviceService.create_device(
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
    d_spine = await DeviceService.create_device(
        test_db,
        DeviceCreate(
            hostname="SW-SPINE-01",
            management_ip="10.100.0.11",
            device_type=DeviceType.SPINE_SWITCH,
            vendor="Arista",
            model="DCS-7050",
            os_type="arista_eos",
            os_version="4.30",
        )
    )
    d_leaf = await DeviceService.create_device(
        test_db,
        DeviceCreate(
            hostname="SW-LEAF-01",
            management_ip="10.100.0.21",
            device_type=DeviceType.LEAF_SWITCH,
            vendor="Arista",
            model="DCS-7050",
            os_type="arista_eos",
            os_version="4.30",
        )
    )

    # Trace path from Core to Leaf
    trace_req = PathTraceRequest(source_device_id=d_core.id, target_device_id=d_leaf.id)
    trace_res = await TopologyService.trace_path(test_db, trace_req)

    assert trace_res.is_path_found is True
    assert trace_res.total_hops == 3  # Core -> Spine -> Leaf
    assert trace_res.primary_path[0].hostname == "RTR-CORE-01"
    assert trace_res.primary_path[-1].hostname == "SW-LEAF-01"


@pytest.mark.asyncio
async def test_spof_and_dependency_analysis(test_db: AsyncSession):
    d_core = await DeviceService.create_device(
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
    d_spine = await DeviceService.create_device(
        test_db,
        DeviceCreate(
            hostname="SW-SPINE-01",
            management_ip="10.100.0.11",
            device_type=DeviceType.SPINE_SWITCH,
            vendor="Arista",
            model="DCS-7050",
            os_type="arista_eos",
            os_version="4.30",
        )
    )
    d_leaf = await DeviceService.create_device(
        test_db,
        DeviceCreate(
            hostname="SW-LEAF-01",
            management_ip="10.100.0.21",
            device_type=DeviceType.LEAF_SWITCH,
            vendor="Arista",
            model="DCS-7050",
            os_type="arista_eos",
            os_version="4.30",
        )
    )

    # Analyze dependencies of Spine
    dep_res = await TopologyService.analyze_dependencies(test_db, d_spine.id)
    assert dep_res.hostname == "SW-SPINE-01"
    assert dep_res.blast_radius_device_count >= 1

    # SPOF Report
    spof_res = await TopologyService.get_spof_report(test_db)
    assert spof_res.network_connectivity_score > 0.0
