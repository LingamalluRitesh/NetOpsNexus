"""
Unit tests for CIS Benchmark Audits and ACL Shadow Analyzer.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.app.database import Base
from backend.app.devices.models import Device, DeviceType, DeviceStatus
from backend.app.devices.schemas import DeviceCreate
from backend.app.devices.service import DeviceService
from backend.app.security.cis_auditor import CisBenchmarkAuditor
from backend.app.security.acl_analyzer import AclShadowAnalyzer
from backend.app.security.models import AclRule
from backend.app.security.schemas import AclRuleBase
from backend.app.security.service import SecurityService
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


def test_cis_benchmark_auditor():
    hardened_cfg = """
    hostname RTR-SEC-01
    aaa new-model
    aaa authentication login default group tacacs+ local
    aaa authorization exec default group tacacs+ local
    service password-encryption
    ip ssh version 2
    control-plane
     service-policy input COPP-POLICY
    ip dhcp snooping
    line vty 0 4
     transport input ssh
     access-class MGMT-IN in
    logging host 10.100.0.50
    service timestamps log datetime msec
    ntp server 10.100.0.100
    """
    score, findings = CisBenchmarkAuditor.audit_cisco_config(hardened_cfg)
    assert score >= 80.0
    assert any(f.check_id == "CIS-1.1" and f.status == "PASS" for f in findings)
    assert any(f.check_id == "CIS-2.1" and f.status == "PASS" for f in findings)


def test_acl_shadow_analyzer():
    rules = [
        AclRule(device_id=1, acl_name="EDGE-FILTER", sequence_num=10, action="deny", protocol="ip", src_ip_prefix="10.0.0.0/8", dst_ip_prefix="any", src_port="any", dst_port="any"),
        AclRule(device_id=1, acl_name="EDGE-FILTER", sequence_num=20, action="permit", protocol="tcp", src_ip_prefix="10.20.0.0/16", dst_ip_prefix="any", src_port="any", dst_port="443"),
        AclRule(device_id=1, acl_name="EDGE-FILTER", sequence_num=30, action="permit", protocol="udp", src_ip_prefix="192.168.1.0/24", dst_ip_prefix="any", src_port="any", dst_port="53"),
    ]
    analyzed = AclShadowAnalyzer.analyze_acl(rules)
    
    # Rule 20 is shadowed by rule 10 (10.20.0.0/16 is inside 10.0.0.0/8)
    assert analyzed[1].sequence_num == 20
    assert analyzed[1].is_shadowed is True
    assert analyzed[1].shadowed_by_sequence == 10

    # Rule 30 is NOT shadowed
    assert analyzed[2].sequence_num == 30
    assert analyzed[2].is_shadowed is False


@pytest.mark.asyncio
async def test_device_security_audit_service(test_db: AsyncSession):
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

    audit_res = await SecurityService.run_device_audit(test_db, device.id)
    assert audit_res.score_percent >= 0.0
    assert len(audit_res.findings) > 0
