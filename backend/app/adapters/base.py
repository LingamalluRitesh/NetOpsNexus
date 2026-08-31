"""
Device Adapter protocol and standardized data structures for hardware communication.
"""

from typing import Protocol, runtime_checkable, List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime


class AdapterSystemInfo(BaseModel):
    hostname: str
    vendor: str
    model: str
    os_type: str
    os_version: str
    serial_number: Optional[str] = None
    uptime_seconds: int
    cpu_percent: float
    memory_percent: float
    temperature_c: Optional[float] = None
    mac_address: Optional[str] = None


class AdapterInterfaceInfo(BaseModel):
    name: str
    description: Optional[str] = None
    if_index: Optional[int] = None
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    subnet_mask: Optional[str] = None
    speed_mbps: int = 1000
    duplex: str = "full"
    mtu: int = 1500
    admin_status: str = "up"
    oper_status: str = "up"
    vlan_id: Optional[int] = None
    is_trunk: bool = False
    rx_bps: float = 0.0
    tx_bps: float = 0.0
    rx_pps: float = 0.0
    tx_pps: float = 0.0
    rx_errors: int = 0
    tx_errors: int = 0
    rx_drops: int = 0
    tx_drops: int = 0


class AdapterRouteInfo(BaseModel):
    destination_prefix: str
    next_hop: str
    protocol: str = "static"
    metric: int = 1
    admin_distance: int = 1
    outgoing_interface: Optional[str] = None


class AdapterNeighborInfo(BaseModel):
    local_interface: str
    neighbor_hostname: str
    neighbor_interface: str
    neighbor_ip: Optional[str] = None
    protocol: str = "lldp"  # lldp, cdp, bgp, ospf


class AdapterCommandResult(BaseModel):
    command: str
    output: str
    exit_code: int = 0
    execution_time_ms: float = 0.0
    status: str = "success"


class AdapterPingResult(BaseModel):
    target: str
    packets_transmitted: int
    packets_received: int
    packet_loss_percent: float
    min_rtt_ms: float
    avg_rtt_ms: float
    max_rtt_ms: float
    stddev_rtt_ms: float
    is_reachable: bool


@runtime_checkable
class DeviceAdapter(Protocol):
    """Unified protocol interface for physical and simulated network device drivers."""

    async def connect(self) -> bool:
        """Establish session / socket connection to target device."""
        ...

    async def disconnect(self) -> bool:
        """Close connection and clean up resources."""
        ...

    async def ping(self, target: Optional[str] = None, count: int = 5, timeout_sec: float = 2.0) -> AdapterPingResult:
        """Measure reachability, RTT latency and packet loss."""
        ...

    async def get_system_info(self) -> AdapterSystemInfo:
        """Retrieve hardware inventory, OS version, CPU, RAM, and thermals."""
        ...

    async def get_interfaces(self) -> List[AdapterInterfaceInfo]:
        """Query physical and logical interface parameters and live traffic counters."""
        ...

    async def get_routes(self) -> List[AdapterRouteInfo]:
        """Extract routing table forwarding information base."""
        ...

    async def get_neighbors(self) -> List[AdapterNeighborInfo]:
        """Discover connected LLDP/CDP neighbor relationships."""
        ...

    async def get_running_config(self) -> str:
        """Fetch running configuration text from device."""
        ...

    async def apply_config(self, config_text: str) -> AdapterCommandResult:
        """Deploy configuration lines to device."""
        ...

    async def execute_command(self, command: str) -> AdapterCommandResult:
        """Execute arbitrary CLI command (e.g., 'show ip route', 'show bgp summary')."""
        ...
