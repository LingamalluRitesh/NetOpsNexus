"""
Unit tests for Automation Action Catalog and DAG execution engine.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.devices.models import Device, DeviceType, DeviceStatus
from backend.app.devices.schemas import DeviceCreate
from backend.app.devices.service import DeviceService
from backend.app.automation.models import Workflow, WorkflowRun, TriggerType, WorkflowRunStatus
from backend.app.automation.schemas import WorkflowNode, WorkflowEdge, WorkflowDefinition, WorkflowCreate
from backend.app.automation.action_catalog import ActionCatalog
from backend.app.automation.dag_engine import DagEngine
from backend.app.automation.service import AutomationService
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


def test_action_catalog_listing():
    actions = ActionCatalog.list_actions()
    action_names = [a.action_name for a in actions]
    assert "cli.execute_command" in action_names
    assert "config.backup" in action_names
    assert "interface.set_state" in action_names
    assert "diagnostic.run_ping" in action_names
    assert "notification.webhook" in action_names


@pytest.mark.asyncio
async def test_dag_workflow_execution(test_db: AsyncSession):
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

    # Build DAG: Trigger -> Backup Config -> Show Routes -> Ping Test
    definition = WorkflowDefinition(
        nodes=[
            WorkflowNode(id="node_trig", type="trigger", label="Manual Trigger"),
            WorkflowNode(id="node_backup", type="action", label="Backup Config", action_name="config.backup", parameters={"device_id": device.id}),
            WorkflowNode(id="node_cli", type="action", label="Show Routes", action_name="cli.execute_command", parameters={"device_id": device.id, "command": "show ip route"}),
            WorkflowNode(id="node_ping", type="action", label="Ping Test", action_name="diagnostic.run_ping", parameters={"source_device_id": device.id, "target_ip": "10.100.0.2"}),
        ],
        edges=[
            WorkflowEdge(id="e1", source="node_trig", target="node_backup"),
            WorkflowEdge(id="e2", source="node_backup", target="node_cli"),
            WorkflowEdge(id="e3", source="node_cli", target="node_ping"),
        ]
    )

    wf_create = WorkflowCreate(
        name="Pre-Maintenance Health & Backup Sweep",
        description="Takes backup, checks routes, and verifies reachability",
        trigger_type=TriggerType.MANUAL,
        definition=definition,
    )
    workflow = await AutomationService.create_workflow(test_db, wf_create)
    assert workflow.id is not None

    # Run workflow
    run = await AutomationService.trigger_workflow(test_db, workflow.id)
    assert run.status == WorkflowRunStatus.SUCCESS
    assert len(run.step_logs) >= 3
    assert any(log.action_name == "config.backup" and log.status == "success" for log in run.step_logs)
    assert any(log.action_name == "cli.execute_command" and log.status == "success" for log in run.step_logs)
