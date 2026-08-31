"""
Unit tests for IPAM Subnets, IP address allocation, and conflict detection.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.devices.models import Device, Site, NetworkInterface
from backend.app.ipam.models import Subnet, IpAddress, IpConflict, IpStatus, SubnetStatus
from backend.app.ipam.schemas import SubnetCreate, SubnetSplitRequest, IpAddressCreate
from backend.app.ipam.service import IpamService
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
async def test_subnet_creation_and_listing(test_db: AsyncSession):
    subnet_data = SubnetCreate(
        name="Data Center Workstations",
        network_address="10.20.10.0",
        prefix_len=24,
        ip_version=4,
        description="Engineering workstations pool",
    )
    subnet = await IpamService.create_subnet(test_db, subnet_data)
    assert subnet.id is not None
    assert subnet.total_ips == 256
    assert subnet.reserved_ips == 1  # default gateway
    assert subnet.available_ips == 255

    subnets = await IpamService.list_subnets(test_db)
    assert len(subnets) >= 1
    assert subnets[0].name == "Data Center Workstations"


@pytest.mark.asyncio
async def test_ip_allocation_and_conflict(test_db: AsyncSession):
    subnet = await IpamService.create_subnet(
        test_db,
        SubnetCreate(
            name="Servers VLAN",
            network_address="10.30.0.0",
            prefix_len=24,
        )
    )

    # Allocate IP
    alloc_data = IpAddressCreate(
        subnet_id=subnet.id,
        address="10.30.0.10",
        status=IpStatus.ALLOCATED,
        mac_address="00:11:22:33:44:55",
        fqdn="srv-app-01.corp.local",
    )
    ip_res = await IpamService.allocate_ip(test_db, alloc_data)
    assert ip_res.id is not None
    assert ip_res.address == "10.30.0.10"

    # Attempt to allocate duplicate IP with different MAC -> must detect conflict
    conflict_data = IpAddressCreate(
        subnet_id=subnet.id,
        address="10.30.0.10",
        status=IpStatus.ALLOCATED,
        mac_address="AA:BB:CC:DD:EE:FF",
        fqdn="srv-rogue-01.corp.local",
    )
    with pytest.raises(Exception):
        await IpamService.allocate_ip(test_db, conflict_data)

    conflicts = await IpamService.list_conflicts(test_db)
    assert len(conflicts) >= 1
    assert conflicts[0].ip_address == "10.30.0.10"


@pytest.mark.asyncio
async def test_subnet_split_service(test_db: AsyncSession):
    subnet = await IpamService.create_subnet(
        test_db,
        SubnetCreate(
            name="Branch Office LAN",
            network_address="10.50.0.0",
            prefix_len=24,
        )
    )

    # Split /24 into /25s
    split_req = SubnetSplitRequest(subnet_id=subnet.id, new_prefix_len=25)
    children = await IpamService.split_subnet(test_db, split_req)
    assert len(children) == 2
    assert children[0].prefix_len == 25
    assert children[1].prefix_len == 25
