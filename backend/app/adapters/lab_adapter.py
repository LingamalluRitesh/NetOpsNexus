"""
LabNetworkAdapter: Enterprise carrier-grade network simulation subsystem.
Provides realistic multi-tier topology simulation, dynamic telemetry fluctuations,
BGP/OSPF adjacencies, interface counters, and authentic multi-vendor CLI emulation.
"""

from typing import List, Optional, Dict, Any
import math
import random
import time
from datetime import datetime, timezone
from backend.app.adapters.base import (
    DeviceAdapter, AdapterSystemInfo, AdapterInterfaceInfo, AdapterRouteInfo,
    AdapterNeighborInfo, AdapterCommandResult, AdapterPingResult
)


class LabDeviceState:
    """State container for a simulated network device."""
    def __init__(
        self,
        hostname: str,
        management_ip: str,
        device_type: str,
        vendor: str,
        model: str,
        os_type: str,
        os_version: str,
        mac_address: str,
        site_code: str,
        interfaces: List[Dict[str, Any]],
        routes: List[Dict[str, Any]],
        neighbors: List[Dict[str, Any]],
        initial_config: str,
    ):
        self.hostname = hostname
        self.management_ip = management_ip
        self.device_type = device_type
        self.vendor = vendor
        self.model = model
        self.os_type = os_type
        self.os_version = os_version
        self.mac_address = mac_address
        self.site_code = site_code
        self.interfaces = interfaces
        self.routes = routes
        self.neighbors = neighbors
        self.running_config = initial_config
        self.boot_time = time.time() - (86400 * random.randint(3, 45))
        self.base_cpu = random.uniform(10.0, 35.0)
        self.base_mem = random.uniform(30.0, 60.0)
        self.is_flapping = False
        self.injected_latency_ms = 0.0
        self.injected_loss_pct = 0.0


class LabNetworkAdapter:
    """Enterprise Lab simulation adapter fulfilling DeviceAdapter protocol."""

    # In-memory registry of all simulated devices across the enterprise network
    _device_registry: Dict[str, LabDeviceState] = {}

    def __init__(self, target_host_or_ip: str):
        self.target = target_host_or_ip
        self._ensure_devices_initialized()
        self.state = self._find_device_state(target_host_or_ip)

    @classmethod
    def _ensure_devices_initialized(cls):
        if cls._device_registry:
            return

        # Seed realistic enterprise infrastructure
        devices = [
            # HQ Core & Spines
            LabDeviceState(
                hostname="RTR-CORE-01",
                management_ip="10.100.0.1",
                device_type="core_router",
                vendor="Cisco Systems",
                model="Catalyst 8500-12X",
                os_type="cisco_ios",
                os_version="17.9.4a",
                mac_address="00:50:56:A1:01:01",
                site_code="HQ-DC",
                interfaces=[
                    {"name": "HundredGigE1/0/1", "desc": "Uplink to ISP-1 Tier-1", "speed": 100000, "ip": "198.51.100.2", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "HundredGigE1/0/2", "desc": "Inter-Core Peering to RTR-CORE-02", "speed": 100000, "ip": "10.100.255.1", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "FortyGigE1/1/1", "desc": "Trunk to SW-SPINE-01", "speed": 40000, "ip": "10.100.1.1", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "FortyGigE1/1/2", "desc": "Trunk to SW-SPINE-02", "speed": 40000, "ip": "10.100.1.5", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "TenGigE2/0/1", "desc": "WAN Link to RTR-CAMPUS-01", "speed": 10000, "ip": "10.200.1.1", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "GigabitEthernet0", "desc": "Out-of-Band Management", "speed": 1000, "ip": "10.100.0.1", "mask": "255.255.255.0", "oper": "up"},
                ],
                routes=[
                    {"prefix": "0.0.0.0/0", "next_hop": "198.51.100.1", "proto": "bgp", "metric": 0, "ad": 20},
                    {"prefix": "10.0.0.0/8", "next_hop": "10.100.255.2", "proto": "bgp", "metric": 10, "ad": 200},
                    {"prefix": "10.100.0.0/16", "next_hop": "0.0.0.0", "proto": "direct", "metric": 0, "ad": 0},
                    {"prefix": "10.200.0.0/16", "next_hop": "10.200.1.2", "proto": "ospf", "metric": 20, "ad": 110},
                ],
                neighbors=[
                    {"local": "HundredGigE1/0/2", "hostname": "RTR-CORE-02", "remote": "HundredGigE1/0/2", "ip": "10.100.255.2", "proto": "bgp"},
                    {"local": "FortyGigE1/1/1", "hostname": "SW-SPINE-01", "remote": "HundredGigE0/1", "ip": "10.100.1.2", "proto": "lldp"},
                    {"local": "FortyGigE1/1/2", "hostname": "SW-SPINE-02", "remote": "HundredGigE0/1", "ip": "10.100.1.6", "proto": "lldp"},
                    {"local": "TenGigE2/0/1", "hostname": "RTR-CAMPUS-01", "remote": "TenGigE0/0/1", "ip": "10.200.1.2", "proto": "ospf"},
                ],
                initial_config="!\nhostname RTR-CORE-01\n!\nrouter bgp 65000\n bgp router-id 10.100.0.1\n neighbor 198.51.100.1 remote-as 701\n neighbor 10.100.255.2 remote-as 65000\n!\ninterface HundredGigE1/0/1\n description Uplink to ISP-1\n ip address 198.51.100.2 255.255.255.252\n no shutdown\n!\nend\n"
            ),
            LabDeviceState(
                hostname="RTR-CORE-02",
                management_ip="10.100.0.2",
                device_type="core_router",
                vendor="Cisco Systems",
                model="Catalyst 8500-12X",
                os_type="cisco_ios",
                os_version="17.9.4a",
                mac_address="00:50:56:A1:01:02",
                site_code="HQ-DC",
                interfaces=[
                    {"name": "HundredGigE1/0/1", "desc": "Uplink to ISP-2 Tier-1", "speed": 100000, "ip": "203.0.113.2", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "HundredGigE1/0/2", "desc": "Inter-Core Peering to RTR-CORE-01", "speed": 100000, "ip": "10.100.255.2", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "FortyGigE1/1/1", "desc": "Trunk to SW-SPINE-01", "speed": 40000, "ip": "10.100.1.9", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "FortyGigE1/1/2", "desc": "Trunk to SW-SPINE-02", "speed": 40000, "ip": "10.100.1.13", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "GigabitEthernet0", "desc": "Out-of-Band Management", "speed": 1000, "ip": "10.100.0.2", "mask": "255.255.255.0", "oper": "up"},
                ],
                routes=[
                    {"prefix": "0.0.0.0/0", "next_hop": "203.0.113.1", "proto": "bgp", "metric": 0, "ad": 20},
                    {"prefix": "10.100.0.0/16", "next_hop": "0.0.0.0", "proto": "direct", "metric": 0, "ad": 0},
                ],
                neighbors=[
                    {"local": "HundredGigE1/0/2", "hostname": "RTR-CORE-01", "remote": "HundredGigE1/0/2", "ip": "10.100.255.1", "proto": "bgp"},
                    {"local": "FortyGigE1/1/1", "hostname": "SW-SPINE-01", "remote": "HundredGigE0/2", "ip": "10.100.1.10", "proto": "lldp"},
                ],
                initial_config="!\nhostname RTR-CORE-02\n!\nrouter bgp 65000\n neighbor 203.0.113.1 remote-as 3356\n neighbor 10.100.255.1 remote-as 65000\n!\nend\n"
            ),
            LabDeviceState(
                hostname="SW-SPINE-01",
                management_ip="10.100.0.11",
                device_type="spine_switch",
                vendor="Arista Networks",
                model="DCS-7050X3-48YC12",
                os_type="arista_eos",
                os_version="4.30.2F",
                mac_address="00:1C:73:B2:11:01",
                site_code="HQ-DC",
                interfaces=[
                    {"name": "HundredGigE0/1", "desc": "Uplink to RTR-CORE-01", "speed": 100000, "ip": "10.100.1.2", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "HundredGigE0/2", "desc": "Uplink to RTR-CORE-02", "speed": 100000, "ip": "10.100.1.10", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "HundredGigE0/3", "desc": "Downlink to SW-LEAF-01", "speed": 100000, "ip": "10.100.2.1", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "HundredGigE0/4", "desc": "Downlink to SW-LEAF-02", "speed": 100000, "ip": "10.100.2.5", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "HundredGigE0/5", "desc": "Downlink to SW-LEAF-03", "speed": 100000, "ip": "10.100.2.9", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "HundredGigE0/6", "desc": "Downlink to SW-LEAF-04", "speed": 100000, "ip": "10.100.2.13", "mask": "255.255.255.252", "oper": "up"},
                ],
                routes=[
                    {"prefix": "10.100.0.0/16", "next_hop": "0.0.0.0", "proto": "direct", "metric": 0, "ad": 0},
                ],
                neighbors=[
                    {"local": "HundredGigE0/1", "hostname": "RTR-CORE-01", "remote": "FortyGigE1/1/1", "proto": "lldp"},
                    {"local": "HundredGigE0/3", "hostname": "SW-LEAF-01", "remote": "HundredGigE0/1", "proto": "lldp"},
                ],
                initial_config="! Arista EOS Configuration\nhostname SW-SPINE-01\n!\ninterface HundredGigE0/1\n switchport mode routed\n!\n"
            ),
            LabDeviceState(
                hostname="SW-LEAF-01",
                management_ip="10.100.0.21",
                device_type="leaf_switch",
                vendor="Arista Networks",
                model="DCS-7050SX3-48YC8",
                os_type="arista_eos",
                os_version="4.30.2F",
                mac_address="00:1C:73:C3:21:01",
                site_code="HQ-DC",
                interfaces=[
                    {"name": "HundredGigE0/1", "desc": "Uplink to SW-SPINE-01", "speed": 100000, "ip": "10.100.2.2", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "TwentyFiveGigE1/1", "desc": "Compute Host SRV-APP-01", "speed": 25000, "ip": "10.100.10.11", "mask": "255.255.255.0", "oper": "up"},
                    {"name": "TwentyFiveGigE1/2", "desc": "Compute Host SRV-DB-01", "speed": 25000, "ip": "10.100.10.12", "mask": "255.255.255.0", "oper": "up"},
                ],
                routes=[],
                neighbors=[{"local": "HundredGigE0/1", "hostname": "SW-SPINE-01", "remote": "HundredGigE0/3", "proto": "lldp"}],
                initial_config="! SW-LEAF-01 EOS Config\nhostname SW-LEAF-01\n"
            ),
            LabDeviceState(
                hostname="FW-DC-PRI-01",
                management_ip="10.100.0.50",
                device_type="firewall",
                vendor="Palo Alto Networks",
                model="PA-5450",
                os_type="panos",
                os_version="11.1.2",
                mac_address="00:90:7F:88:50:01",
                site_code="HQ-DC",
                interfaces=[
                    {"name": "ethernet1/1", "desc": "Untrust WAN", "speed": 40000, "ip": "198.51.100.10", "mask": "255.255.255.248", "oper": "up"},
                    {"name": "ethernet1/2", "desc": "Trust DC LAN", "speed": 40000, "ip": "10.100.10.1", "mask": "255.255.255.0", "oper": "up"},
                    {"name": "ethernet1/3", "desc": "DMZ Zone", "speed": 10000, "ip": "172.16.50.1", "mask": "255.255.255.0", "oper": "up"},
                ],
                routes=[
                    {"prefix": "0.0.0.0/0", "next_hop": "198.51.100.9", "proto": "static", "metric": 10, "ad": 10},
                ],
                neighbors=[],
                initial_config="set deviceconfig system hostname FW-DC-PRI-01\nset network interface ethernet ethernet1/1 layer3\n"
            ),
            LabDeviceState(
                hostname="RTR-CAMPUS-01",
                management_ip="10.200.0.1",
                device_type="edge_router",
                vendor="Juniper Networks",
                model="MX204",
                os_type="juniper_junos",
                os_version="23.2R1-S1",
                mac_address="00:05:85:D4:01:01",
                site_code="SJC-CAMPUS",
                interfaces=[
                    {"name": "xe-0/0/0", "desc": "WAN Link to HQ Core", "speed": 10000, "ip": "10.200.1.2", "mask": "255.255.255.252", "oper": "up"},
                    {"name": "xe-0/0/1", "desc": "Trunk to SW-DIST-01", "speed": 10000, "ip": "10.200.10.1", "mask": "255.255.255.0", "oper": "up"},
                ],
                routes=[
                    {"prefix": "0.0.0.0/0", "next_hop": "10.200.1.1", "proto": "ospf", "metric": 20, "ad": 110},
                ],
                neighbors=[
                    {"local": "xe-0/0/0", "hostname": "RTR-CORE-01", "remote": "TenGigE2/0/1", "proto": "ospf"}
                ],
                initial_config="system { host-name RTR-CAMPUS-01; }\ninterfaces { xe-0/0/0 { unit 0 { family inet; } } }\n"
            ),
            LabDeviceState(
                hostname="SW-DIST-01",
                management_ip="10.200.0.11",
                device_type="distribution_switch",
                vendor="Cisco Systems",
                model="Catalyst 9500-48Y4C",
                os_type="cisco_ios",
                os_version="17.9.4a",
                mac_address="00:2A:6A:11:01:01",
                site_code="SJC-CAMPUS",
                interfaces=[
                    {"name": "TenGigabitEthernet1/0/1", "desc": "Uplink to RTR-CAMPUS-01", "speed": 10000, "ip": "10.200.10.2", "mask": "255.255.255.0", "oper": "up"},
                    {"name": "TenGigabitEthernet1/0/2", "desc": "Downlink to SW-ACC-01", "speed": 10000, "ip": "10.200.20.1", "mask": "255.255.255.0", "oper": "up"},
                ],
                routes=[],
                neighbors=[{"local": "TenGigabitEthernet1/0/1", "hostname": "RTR-CAMPUS-01", "remote": "xe-0/0/1", "proto": "lldp"}],
                initial_config="hostname SW-DIST-01\n"
            ),
            LabDeviceState(
                hostname="SW-ACC-01",
                management_ip="10.200.0.21",
                device_type="access_switch",
                vendor="Cisco Systems",
                model="Catalyst 9300-48P",
                os_type="cisco_ios",
                os_version="17.9.4a",
                mac_address="00:2A:6A:21:01:01",
                site_code="SJC-CAMPUS",
                interfaces=[
                    {"name": "GigabitEthernet1/0/1", "desc": "Uplink to SW-DIST-01", "speed": 10000, "oper": "up"},
                    {"name": "GigabitEthernet1/0/2", "desc": "Access Floor 1 Workstations", "speed": 1000, "oper": "up"},
                    {"name": "GigabitEthernet1/0/48", "desc": "PoE Uplink to WAP-FLOOR1-01", "speed": 1000, "oper": "up"},
                ],
                routes=[],
                neighbors=[{"local": "GigabitEthernet1/0/1", "hostname": "SW-DIST-01", "remote": "TenGigabitEthernet1/0/2", "proto": "lldp"}],
                initial_config="hostname SW-ACC-01\n"
            ),
            LabDeviceState(
                hostname="WAP-FLOOR1-01",
                management_ip="10.200.0.101",
                device_type="wireless_ap",
                vendor="Cisco Systems",
                model="Catalyst 9130AX",
                os_type="cisco_ios",
                os_version="17.9.4a",
                mac_address="00:3E:E1:10:01:01",
                site_code="SJC-CAMPUS",
                interfaces=[
                    {"name": "GigabitEthernet0", "desc": "PoE Uplink to SW-ACC-01", "speed": 1000, "oper": "up"},
                    {"name": "Radio0", "desc": "2.4GHz 802.11ax", "speed": 1200, "oper": "up"},
                    {"name": "Radio1", "desc": "5GHz 802.11ax", "speed": 4800, "oper": "up"},
                ],
                routes=[],
                neighbors=[{"local": "GigabitEthernet0", "hostname": "SW-ACC-01", "remote": "GigabitEthernet1/0/48", "proto": "lldp"}],
                initial_config="hostname WAP-FLOOR1-01\n"
            ),
            LabDeviceState(
                hostname="RTR-BR-LON-01",
                management_ip="10.300.0.1",
                device_type="gateway",
                vendor="Cisco Systems",
                model="ISR 4451",
                os_type="cisco_ios",
                os_version="17.9.4a",
                mac_address="00:70:89:30:01:01",
                site_code="LON-BRANCH",
                interfaces=[
                    {"name": "GigabitEthernet0/0/0", "desc": "SD-WAN Internet", "speed": 1000, "ip": "195.55.10.2", "mask": "255.255.255.248", "oper": "up"},
                    {"name": "GigabitEthernet0/0/1", "desc": "LAN Trunk to SW-BR-LON-01", "speed": 1000, "ip": "10.300.10.1", "mask": "255.255.255.0", "oper": "up"},
                ],
                routes=[
                    {"prefix": "0.0.0.0/0", "next_hop": "195.55.10.1", "proto": "bgp", "metric": 10, "ad": 20},
                    {"prefix": "10.0.0.0/8", "next_hop": "195.55.10.1", "proto": "ospf", "metric": 50, "ad": 110},
                ],
                neighbors=[{"local": "GigabitEthernet0/0/1", "hostname": "SW-BR-LON-01", "remote": "GigabitEthernet0/1", "proto": "lldp"}],
                initial_config="hostname RTR-BR-LON-01\n"
            ),
        ]

        for dev in devices:
            cls._device_registry[dev.hostname] = dev
            cls._device_registry[dev.management_ip] = dev

    def _find_device_state(self, key: str) -> LabDeviceState:
        if key in self._device_registry:
            return self._device_registry[key]
        
        # Synthesize fallback on demand
        state = LabDeviceState(
            hostname=f"LAB-{key.replace('.', '-')}",
            management_ip=key if "." in key else "10.99.99.1",
            device_type="access_switch",
            vendor="Cisco Systems",
            model="Catalyst 9200L",
            os_type="cisco_ios",
            os_version="17.9.4a",
            mac_address="00:50:56:FF:EE:DD",
            site_code="HQ-DC",
            interfaces=[
                {"name": "GigabitEthernet0/1", "desc": "Uplink", "speed": 1000, "oper": "up"},
                {"name": "GigabitEthernet0/2", "desc": "Access", "speed": 1000, "oper": "up"},
            ],
            routes=[],
            neighbors=[],
            initial_config=f"hostname LAB-{key.replace('.', '-')}\n"
        )
        self._device_registry[key] = state
        return state

    async def connect(self) -> bool:
        return True

    async def disconnect(self) -> bool:
        return True

    async def ping(self, target: Optional[str] = None, count: int = 5, timeout_sec: float = 2.0) -> AdapterPingResult:
        # Realistic latency with small jitter
        base_latency = 0.8 + self.state.injected_latency_ms
        if "LON" in self.state.hostname:
            base_latency += 72.0  # Transatlantic latency

        loss = self.state.injected_loss_pct
        received = int(count * (1.0 - (loss / 100.0)))
        
        avg_rtt = base_latency + random.uniform(0.1, 0.5)
        min_rtt = max(0.2, avg_rtt - random.uniform(0.1, 0.3))
        max_rtt = avg_rtt + random.uniform(0.2, 1.2)

        return AdapterPingResult(
            target=target or self.target,
            packets_transmitted=count,
            packets_received=received,
            packet_loss_percent=loss,
            min_rtt_ms=round(min_rtt, 2),
            avg_rtt_ms=round(avg_rtt, 2),
            max_rtt_ms=round(max_rtt, 2),
            stddev_rtt_ms=round(random.uniform(0.05, 0.25), 2),
            is_reachable=received > 0,
        )

    async def get_system_info(self) -> AdapterSystemInfo:
        now = time.time()
        # Sine wave diurnal fluctuation
        hour = (datetime.now(timezone.utc).hour) % 24
        diurnal_factor = 0.5 + 0.5 * math.sin(math.pi * (hour - 6) / 12)
        
        cpu = min(98.0, self.state.base_cpu + (diurnal_factor * 25.0) + random.uniform(-3.0, 4.0))
        mem = min(95.0, self.state.base_mem + (diurnal_factor * 15.0) + random.uniform(-1.0, 2.0))
        temp = 32.0 + (cpu * 0.2) + random.uniform(-0.5, 0.5)

        return AdapterSystemInfo(
            hostname=self.state.hostname,
            vendor=self.state.vendor,
            model=self.state.model,
            os_type=self.state.os_type,
            os_version=self.state.os_version,
            serial_number=f"SN-{self.state.hostname}-2026",
            uptime_seconds=int(now - self.state.boot_time),
            cpu_percent=round(cpu, 1),
            memory_percent=round(mem, 1),
            temperature_c=round(temp, 1),
            mac_address=self.state.mac_address,
        )

    async def get_interfaces(self) -> List[AdapterInterfaceInfo]:
        results = []
        hour = (datetime.now(timezone.utc).hour) % 24
        # Positive diurnal curve: peak at midday, lower at night, minimum 0.15
        diurnal_factor = max(0.15, 0.2 + 0.8 * ((math.sin(math.pi * (hour - 6) / 12) + 1.0) / 2.0))

        for i, iface in enumerate(self.state.interfaces, start=1):
            speed_mbps = iface.get("speed", 1000)
            max_bps = speed_mbps * 1_000_000 * 0.75  # ~75% max load
            
            # Baseline traffic with diurnal variation
            rx_bps = max_bps * diurnal_factor * random.uniform(0.4, 0.85)
            tx_bps = max_bps * diurnal_factor * random.uniform(0.3, 0.80)
            
            rx_pps = rx_bps / (8 * 1200)  # avg 1200 byte frame
            tx_pps = tx_bps / (8 * 1200)

            # Simulated intermittent errors on specific ports
            rx_err = random.randint(0, 3) if self.state.is_flapping else 0
            tx_err = random.randint(0, 2) if self.state.is_flapping else 0
            rx_drop = random.randint(0, 5) if self.state.injected_loss_pct > 0 else 0

            results.append(
                AdapterInterfaceInfo(
                    name=iface["name"],
                    description=iface.get("desc"),
                    if_index=i,
                    mac_address=f"{self.state.mac_address[:-2]}{i:02X}",
                    ip_address=iface.get("ip"),
                    subnet_mask=iface.get("mask"),
                    speed_mbps=speed_mbps,
                    duplex="full",
                    mtu=1500,
                    admin_status="up",
                    oper_status=iface.get("oper", "up"),
                    is_trunk=iface.get("speed", 1000) >= 10000,
                    rx_bps=round(rx_bps, 1),
                    tx_bps=round(tx_bps, 1),
                    rx_pps=round(rx_pps, 1),
                    tx_pps=round(tx_pps, 1),
                    rx_errors=rx_err,
                    tx_errors=tx_err,
                    rx_drops=rx_drop,
                    tx_drops=0,
                )
            )
        return results

    async def get_routes(self) -> List[AdapterRouteInfo]:
        return [
            AdapterRouteInfo(
                destination_prefix=r["prefix"],
                next_hop=r["next_hop"],
                protocol=r.get("proto", "static"),
                metric=r.get("metric", 1),
                admin_distance=r.get("ad", 1),
                outgoing_interface=r.get("out_if"),
            )
            for r in self.state.routes
        ]

    async def get_neighbors(self) -> List[AdapterNeighborInfo]:
        return [
            AdapterNeighborInfo(
                local_interface=n["local"],
                neighbor_hostname=n["hostname"],
                neighbor_interface=n["remote"],
                neighbor_ip=n.get("ip"),
                protocol=n.get("proto", "lldp"),
            )
            for n in self.state.neighbors
        ]

    async def get_running_config(self) -> str:
        return self.state.running_config

    async def apply_config(self, config_text: str) -> AdapterCommandResult:
        start = time.time()
        # Update in-memory state
        self.state.running_config = config_text
        return AdapterCommandResult(
            command="configure terminal",
            output=f"[{self.state.hostname}#] Configuration successfully applied and verified in running-config.",
            exit_code=0,
            execution_time_ms=round((time.time() - start) * 1000, 2),
            status="success"
        )

    async def execute_command(self, command: str) -> AdapterCommandResult:
        start = time.time()
        cmd = command.strip().lower()
        
        if "show version" in cmd or "show ver" in cmd:
            output = (
                f"{self.state.vendor} IOS-XE Software, Version {self.state.os_version}\n"
                f"{self.state.hostname} uptime is 14 weeks, 2 days, 4 hours\n"
                f"System image file is \"bootflash:packages.conf\"\n"
                f"cisco {self.state.model} processor with 16777216K bytes of physical memory.\n"
                f"Processor board ID {self.state.mac_address}\n"
            )
        elif "show running-config" in cmd:
            output = self.state.running_config
        elif "show ip interface brief" in cmd or "show int brief" in cmd:
            lines = ["Interface                  IP-Address      OK? Method Status                Protocol"]
            for iface in self.state.interfaces:
                ip = iface.get("ip", "unassigned")
                lines.append(f"{iface['name']:<26} {ip:<15} YES manual up                    up")
            output = "\n".join(lines)
        elif "show ip route" in cmd or "show route" in cmd:
            lines = [f"Routing Table: {self.state.hostname}", "Gateway of last resort is 10.100.0.1 to network 0.0.0.0\n"]
            for r in self.state.routes:
                lines.append(f"{r.get('proto', 'S').upper():<4} {r['prefix']:<18} via {r['next_hop']}")
            output = "\n".join(lines)
        elif "show ip bgp summary" in cmd or "show bgp summary" in cmd:
            output = (
                f"BGP router identifier {self.state.management_ip}, local AS number 65000\n"
                "Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd\n"
                "198.51.100.1    4   701   48123   48119       12    0    0 14w2d    Establish (425890)\n"
                "10.100.255.2    4 65000   94120   94118       12    0    0 06w1d    Establish (12)\n"
            )
        elif "show lldp neighbors" in cmd:
            lines = ["Capability codes: (R) Router, (B) Bridge, (W) WLAN, (S) Station\nDevice ID        Local Intf          Hold-time  Capability      Port ID"]
            for n in self.state.neighbors:
                lines.append(f"{n['hostname']:<16} {n['local']:<19} 120        R B             {n['remote']}")
            output = "\n".join(lines)
        else:
            output = f"{self.state.hostname}# {command}\nCommand executed successfully in virtual environment."

        return AdapterCommandResult(
            command=command,
            output=output,
            exit_code=0,
            execution_time_ms=round((time.time() - start) * 1000, 2),
            status="success"
        )
