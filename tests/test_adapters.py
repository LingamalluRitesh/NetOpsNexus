"""
Unit tests for DeviceAdapter drivers: SNMPAdapter, SSHAdapter, and ICMPAdapter.
"""

import pytest
from backend.app.adapters.icmp_adapter import ICMPAdapter
from backend.app.adapters.snmp_adapter import SNMPAdapter
from backend.app.adapters.ssh_adapter import SSHAdapter
from backend.app.adapters.manager import AdapterManager


@pytest.mark.asyncio
async def test_icmp_adapter_local_ping():
    adapter = ICMPAdapter("127.0.0.1")
    result = await adapter.ping(count=2, timeout_sec=1.0)
    assert result.packets_transmitted == 2
    assert result.is_reachable is True
    assert result.avg_rtt_ms >= 0.0


@pytest.mark.asyncio
async def test_snmp_adapter():
    adapter = SNMPAdapter("10.100.0.1", community="public")
    assert await adapter.connect() is True
    sys_info = await adapter.get_system_info()
    assert sys_info.hostname is not None
    assert sys_info.cpu_percent >= 0.0
    ifaces = await adapter.get_interfaces()
    assert len(ifaces) > 0


@pytest.mark.asyncio
async def test_ssh_adapter_cli_execution():
    adapter = SSHAdapter("10.100.0.1", username="admin")
    res = await adapter.execute_command("show ip route")
    assert res.status == "success"
    assert "Gateway of last resort" in res.output
    assert res.execution_time_ms >= 0.0


def test_adapter_manager_factory():
    ad_lab = AdapterManager.get_adapter("10.100.0.1", force_lab=True)
    assert ad_lab is not None
    
    ad_ssh = AdapterManager.get_adapter("10.100.0.1", driver="ssh", force_lab=False)
    assert isinstance(ad_ssh, SSHAdapter)
