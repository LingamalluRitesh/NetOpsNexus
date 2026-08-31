"""
Unit tests for LabNetworkAdapter realistic carrier-grade multi-tier simulation.
"""

import pytest
from backend.app.adapters.lab_adapter import LabNetworkAdapter


@pytest.mark.asyncio
async def test_lab_adapter_core_router():
    adapter = LabNetworkAdapter("RTR-CORE-01")
    sys_info = await adapter.get_system_info()
    assert sys_info.hostname == "RTR-CORE-01"
    assert sys_info.vendor == "Cisco Systems"
    assert sys_info.model == "Catalyst 8500-12X"
    assert sys_info.cpu_percent > 0.0
    assert sys_info.uptime_seconds > 0

    # Test interfaces
    ifaces = await adapter.get_interfaces()
    assert len(ifaces) >= 5
    uplink = next((i for i in ifaces if "HundredGigE" in i.name), None)
    assert uplink is not None
    assert uplink.speed_mbps == 100000

    # Test routes
    routes = await adapter.get_routes()
    assert any(r.destination_prefix == "0.0.0.0/0" for r in routes)

    # Test neighbors
    neighbors = await adapter.get_neighbors()
    assert len(neighbors) > 0


@pytest.mark.asyncio
async def test_lab_adapter_cli_emulation():
    adapter = LabNetworkAdapter("RTR-CORE-01")
    res_bgp = await adapter.execute_command("show ip bgp summary")
    assert "BGP router identifier" in res_bgp.output
    assert "Establish" in res_bgp.output

    res_int = await adapter.execute_command("show ip interface brief")
    assert "HundredGigE1/0/1" in res_int.output

    # Config change
    config_res = await adapter.apply_config("!\nhostname RTR-CORE-01\ninterface Loopback0\n ip address 10.255.255.1 255.255.255.255\n!\n")
    assert config_res.status == "success"
    running = await adapter.get_running_config()
    assert "Loopback0" in running
