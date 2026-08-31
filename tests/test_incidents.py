"""
Unit tests for Incident Lifecycle, Assignment, RCA report generation, and MTTR calculation.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.devices.models import Device, DeviceType, DeviceStatus
from backend.app.devices.schemas import DeviceCreate
from backend.app.devices.service import DeviceService
from backend.app.auth.models import User
from backend.app.auth.schemas import UserCreate
from backend.app.auth.service import AuthService
from backend.app.incidents.models import Incident, IncidentSeverity, IncidentPriority, IncidentStatus
from backend.app.incidents.schemas import IncidentCreate, IncidentEventCreate, RcaGenerateRequest
from backend.app.incidents.service import IncidentService
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
async def test_incident_lifecycle_and_assignment(test_db: AsyncSession):
    user = await AuthService.create_user(
        test_db,
        UserCreate(username="engineer1", email="eng1@corp.com", password="EngPassword2026!", full_name="Eng One", roles=["network_engineer"])
    )
    device = await DeviceService.create_device(
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

    # 1. Create Incident
    inc_data = IncidentCreate(
        title="BGP Neighbor Session Flapping",
        description="BGP peering with Tier-1 ISP is dropping packets intermittently",
        severity=IncidentSeverity.CRITICAL,
        priority=IncidentPriority.P1,
        affected_device_id=device.id,
    )
    incident = await IncidentService.create_incident(test_db, inc_data, user_id=user.id)
    assert incident.id is not None
    assert incident.status == IncidentStatus.OPEN

    # 2. Assign to engineer
    assigned = await IncidentService.assign_incident(test_db, incident.id, assign_to_id=user.id, user_id=user.id)
    assert assigned.status == IncidentStatus.INVESTIGATING
    assert assigned.assigned_to_id == user.id

    # 3. Add Investigation Event
    event = await IncidentService.add_event(
        test_db, incident.id, IncidentEventCreate(message="Checked optical fiber signal levels; found CRC burst."), user_id=user.id
    )
    assert event.id is not None

    # 4. Resolve Incident
    resolved = await IncidentService.resolve_incident(test_db, incident.id, notes="Cleaned fiber transceiver and reset BGP peer.", user_id=user.id)
    assert resolved.status == IncidentStatus.RESOLVED
    assert resolved.mttr_seconds is not None

    # 5. Generate RCA
    rca = await IncidentService.generate_rca(
        test_db,
        incident.id,
        RcaGenerateRequest(
            root_cause_summary="Dirty fiber optic cable caused packet loss on ISP uplink.",
            impacted_services=["External Internet Egress"],
            remediation_steps_taken=["Cleaned fiber LC connector", "BGP soft reset"],
            preventative_actions=["Schedule monthly optical power telemetry audit"],
        )
    )
    assert rca["incident_id"] == incident.id
    assert len(rca["preventative_actions"]) == 1
