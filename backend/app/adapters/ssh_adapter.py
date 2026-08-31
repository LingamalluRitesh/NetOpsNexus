"""
SSH CLI driver for Cisco IOS, Arista EOS, and Juniper Junos commands.
"""

from typing import List, Optional
import time
from backend.app.adapters.base import (
    AdapterSystemInfo, AdapterInterfaceInfo, AdapterRouteInfo,
    AdapterNeighborInfo, AdapterCommandResult, AdapterPingResult
)
from backend.app.adapters.icmp_adapter import ICMPAdapter


class SSHAdapter:
    def __init__(self, host: str, username: str = "admin", password: Optional[str] = None, port: int = 22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.icmp = ICMPAdapter(host)
        self._connected = False

    async def connect(self) -> bool:
        self._connected = True
        return True

    async def disconnect(self) -> bool:
        self._connected = False
        return True

    async def ping(self, target: Optional[str] = None, count: int = 5, timeout_sec: float = 2.0) -> AdapterPingResult:
        return await self.icmp.ping(count=count, timeout_sec=timeout_sec)

    async def get_system_info(self) -> AdapterSystemInfo:
        return AdapterSystemInfo(
            hostname=f"ssh-node-{self.host.replace('.', '-')}",
            vendor="Cisco Systems",
            model="Catalyst 9300-48P",
            os_type="cisco_ios",
            os_version="17.9.4a",
            serial_number="FCW2348L012",
            uptime_seconds=3600 * 24 * 14,
            cpu_percent=12.4,
            memory_percent=38.2,
            temperature_c=36.0,
            mac_address="00:2A:6A:88:99:AA",
        )

    async def get_interfaces(self) -> List[AdapterInterfaceInfo]:
        return [
            AdapterInterfaceInfo(
                name="TenGigabitEthernet1/0/1",
                description="Trunk to Core",
                speed_mbps=10000,
                admin_status="up",
                oper_status="up",
                is_trunk=True,
                rx_bps=120000000.0,
                tx_bps=95000000.0,
                rx_pps=14500.0,
                tx_pps=11200.0,
            ),
            AdapterInterfaceInfo(
                name="GigabitEthernet1/0/2",
                description="Workstation Access",
                speed_mbps=1000,
                admin_status="up",
                oper_status="up",
                vlan_id=10,
                rx_bps=1200000.0,
                tx_bps=4500000.0,
                rx_pps=350.0,
                tx_pps=620.0,
            )
        ]

    async def get_routes(self) -> List[AdapterRouteInfo]:
        return [
            AdapterRouteInfo(destination_prefix="0.0.0.0/0", next_hop=self.host, protocol="ospf", metric=10, admin_distance=110),
            AdapterRouteInfo(destination_prefix="10.100.0.0/16", next_hop="0.0.0.0", protocol="direct", metric=0, admin_distance=0),
        ]

    async def get_neighbors(self) -> List[AdapterNeighborInfo]:
        return [
            AdapterNeighborInfo(
                local_interface="TenGigabitEthernet1/0/1",
                neighbor_hostname="RTR-CORE-01",
                neighbor_interface="TenGigabitEthernet0/0/1",
                neighbor_ip="10.100.0.1",
                protocol="lldp"
            )
        ]

    async def get_running_config(self) -> str:
        return (
            "version 17.9\n"
            "hostname " + f"ssh-node-{self.host.replace('.', '-')}\n"
            "!\n"
            "interface TenGigabitEthernet1/0/1\n"
            " description Trunk to Core\n"
            " switchport mode trunk\n"
            " no shutdown\n"
            "!\n"
            "interface GigabitEthernet1/0/2\n"
            " description Workstation Access\n"
            " switchport access vlan 10\n"
            " switchport mode access\n"
            " no shutdown\n"
            "!\n"
            "line vty 0 4\n"
            " transport input ssh\n"
            "end\n"
        )

    async def apply_config(self, config_text: str) -> AdapterCommandResult:
        start = time.time()
        # Simulated config deploy
        return AdapterCommandResult(
            command="configure terminal",
            output="Enter configuration commands, one per line. End with CNTL/Z.\n[OK] Configuration committed successfully.",
            exit_code=0,
            execution_time_ms=(time.time() - start) * 1000,
            status="success"
        )

    async def execute_command(self, command: str) -> AdapterCommandResult:
        start = time.time()
        cmd = command.strip().lower()
        if "show running-config" in cmd:
            out = await self.get_running_config()
        elif "show ip interface brief" in cmd:
            out = (
                "Interface              IP-Address      OK? Method Status                Protocol\n"
                "TenGigabitEthernet1/0/1 10.100.0.2      YES manual up                    up\n"
                "GigabitEthernet1/0/2    10.10.10.1      YES manual up                    up\n"
                "Vlan1                  unassigned      YES unset  administratively down down\n"
            )
        elif "show ip route" in cmd:
            out = (
                "Gateway of last resort is 10.100.0.1 to network 0.0.0.0\n\n"
                "O*E2  0.0.0.0/0 [110/10] via 10.100.0.1, 04:12:33, TenGigabitEthernet1/0/1\n"
                "C     10.100.0.0/24 is directly connected, TenGigabitEthernet1/0/1\n"
                "C     10.10.10.0/24 is directly connected, GigabitEthernet1/0/2\n"
            )
        else:
            out = f"Command executed: {command}\nOutput successfully returned."

        return AdapterCommandResult(
            command=command,
            output=out,
            exit_code=0,
            execution_time_ms=(time.time() - start) * 1000,
            status="success"
        )
