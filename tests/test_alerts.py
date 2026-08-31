"""
Unit tests for Alert Rules, Threshold Evaluation, Suppression Windows, and Acknowledgement.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.devices.models import Device, DeviceType, DeviceStatus
from backend.app.devices.schemas import DeviceCreate
from backend.app.devices.service import DeviceService
from backend.app.alerts.models import AlertRule, Alert, AlertSeverity, AlertStatus
from backend.app.alerts.schemas import AlertRuleCreate, AlertAcknowledgeRequest, AlertSilenceRequest
from backend.app.alerts.rules_engine import AlertRulesEngine
from backend.app.alerts.service import AlertService
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
async def test_alert_rule_evaluation_and_trigger(test_db: AsyncSession):
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

    # 1. Create rule: CPU > 80% -> CRITICAL Alert + Auto Incident
    rule = await AlertService.create_rule(
        test_db,
        AlertRuleCreate(
            name="High Core CPU Utilization",
            metric_name="cpu_percent",
            condition_op="gt",
            threshold_value=80.0,
            severity=AlertSeverity.CRITICAL,
            auto_create_incident=True,
        )
    )
    assert rule.id is not None

    # 2. Evaluate with low CPU -> No alert
    await AlertRulesEngine.evaluate_device_metrics(test_db, device, {"cpu_percent": 45.0})
    alerts = await AlertService.list_alerts(test_db)
    assert len(alerts) == 0

    # 3. Evaluate with high CPU (92%) -> Triggers Alert
    await AlertRulesEngine.evaluate_device_metrics(test_db, device, {"cpu_percent": 92.0})
    alerts = await AlertService.list_alerts(test_db)
    assert len(alerts) == 1
    assert alerts[0].metric_value == 92.0

    # 4. Acknowledge Alert
    acked = await AlertService.acknowledge_alerts(test_db, AlertAcknowledgeRequest(alert_ids=[alerts[0].id]))
    assert len(acked) == 1
    updated_alerts = await AlertService.list_alerts(test_db, status=AlertStatus.ACKNOWLEDGED)
    assert len(updated_alerts) == 1
