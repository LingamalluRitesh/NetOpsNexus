"""
Cisco IOS-XE Network Operating System Driver.
Provides authentic CLI parsing, command execution, structured state inspection,
running-configuration generation, and atomic syntax validation.
"""

from typing import Dict, Any, List, Optional, Tuple
import re
import time
from datetime import datetime, timezone


class CiscoIosXeDriver:
    VENDOR = "Cisco Systems"
    OS_NAME = "Cisco IOS-XE Software"
    DEFAULT_PORT = 22

    def __init__(self, hostname: str, ip_address: str, version: str = "17.09.03a"):
        self.hostname = hostname
        self.ip_address = ip_address
        self.version = version
        self.uptime_seconds = 3456000
        self.privileged_mode = False
        self.config_mode = False

    def generate_banner(self) -> str:
        return f"""
*******************************************************************************
* NetOps Nexus - Enterprise Network Intelligence Simulated Device            *
* Hostname: {self.hostname:<15}  Platform: Cisco Catalyst 9300-48UXM        *
* Management IP: {self.ip_address:<15}  OS: {self.OS_NAME} {self.version:<10} *
* UNAUTHORIZED ACCESS TO THIS NETWORK DEVICE IS STRICTLY PROHIBITED           *
*******************************************************************************
"""

    def parse_show_version(self) -> Dict[str, Any]:
        return {
            "vendor": self.VENDOR,
            "os_name": self.OS_NAME,
            "version": self.version,
            "hostname": self.hostname,
            "chassis": "C9300-48UXM",
            "processor_board_id": f"FOC{abs(hash(self.hostname)) % 100000000:08d}",
            "system_image": f"bootflash:packages.conf",
            "uptime_seconds": self.uptime_seconds,
            "compiled": "Fri 12-May-26 14:22 by mcpre",
            "memory_bytes": 17179869184,  # 16 GB
            "flash_bytes": 32212254720,   # 32 GB
        }

    def parse_show_ip_interface_brief(self, interfaces: List[Dict[str, Any]]) -> str:
        lines = [
            f"Interface              IP-Address      OK? Method Status                Protocol",
            f"--------------------------------------------------------------------------------",
        ]
        for iface in interfaces:
            name = iface.get("name", "GigabitEthernet0/0/0")
            ip = iface.get("ip", "unassigned")
            admin = iface.get("admin_status", "up")
            oper = iface.get("oper_status", "up")
            
            status_str = "up" if admin == "up" else "administratively down"
            proto_str = "up" if oper == "up" else "down"
            lines.append(f"{name:<22} {ip:<15} YES NVRAM  {status_str:<21} {proto_str}")
        return "\n".join(lines)

    def parse_show_ip_route(self, routes: List[Dict[str, Any]]) -> str:
        lines = [
            f"Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP",
            f"       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area",
            f"       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2",
            f"       E1 - OSPF external type 1, E2 - OSPF external type 2",
            f"",
            f"Gateway of last resort is 10.100.0.1 to network 0.0.0.0",
            f"",
            f"S*    0.0.0.0/0 [1/0] via 10.100.0.1, HundredGigE1/0/1",
        ]
        for r in routes:
            proto = r.get("protocol", "O")
            prefix = r.get("prefix", "10.0.0.0/24")
            nexthop = r.get("next_hop", "10.100.0.1")
            cost = r.get("metric", 10)
            iface = r.get("interface", "HundredGigE1/0/1")
            lines.append(f"{proto:<5} {prefix:<18} [110/{cost}] via {nexthop}, 4d18h, {iface}")
        return "\n".join(lines)

    def parse_show_bgp_summary(self, local_as: int, peers: List[Dict[str, Any]]) -> str:
        lines = [
            f"BGP router identifier {self.ip_address}, local AS number {local_as}",
            f"BGP table version is 2489, main routing table version 2489",
            f"7 network entries using 1792 bytes of memory",
            f"14 path entries using 1904 bytes of memory",
            f"",
            f"Neighbor        V           AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd",
            f"---------------------------------------------------------------------------------------",
        ]
        for p in peers:
            nbr = p.get("neighbor_ip", "10.200.0.2")
            as_num = p.get("remote_as", 65002)
            rcvd = p.get("msg_rcvd", 45892)
            sent = p.get("msg_sent", 45890)
            uptime = p.get("uptime", "4w2d")
            pfx = p.get("prefixes_received", 42)
            state = p.get("state", "Established")
            pfx_val = str(pfx) if state == "Established" else state
            lines.append(f"{nbr:<15} 4 {as_num:>12} {rcvd:>7} {sent:>7}     2489    0    0 {uptime:<8} {pfx_val}")
        return "\n".join(lines)

    def parse_show_running_config(self, site_name: str = "HQ-DC") -> str:
        return f"""!
! Last configuration change at 18:42:10 UTC Fri Aug 28 2026 by netops_admin
! NVRAM config last updated at 18:42:12 UTC Fri Aug 28 2026 by netops_admin
!
version 17.9
service timestamps debug datetime msec
service timestamps log datetime msec
service password-encryption
service call-home
platform punt-keepalive disable-kernel-core
!
hostname {self.hostname}
!
boot-start-marker
boot-end-marker
!
vrf definition MGMT
 description Out-of-band management VRF
 address-family ipv4
 exit-address-family
!
aaa new-model
aaa authentication login default local
aaa authorization exec default local
!
ip domain name netops.enterprise.internal
ip name-server 10.100.1.1 10.100.1.2
!
ip routing
ipv6 unicast-routing
!
interface Loopback0
 description Router ID Loopback
 ip address {self.ip_address} 255.255.255.255
 no shutdown
!
interface HundredGigE1/0/1
 description Core Transit Link to Spine
 mtu 9216
 ip address 10.100.0.1 255.255.255.252
 ip ospf 1 area 0
 no shutdown
!
interface HundredGigE1/0/2
 description Inter-DC Backbone Uplink
 mtu 9216
 ip address 10.100.0.5 255.255.255.252
 ip ospf 1 area 0
 no shutdown
!
router ospf 1
 router-id {self.ip_address}
 passive-interface default
 no passive-interface HundredGigE1/0/1
 no passive-interface HundredGigE1/0/2
 max-metric router-lsa on-startup 300
!
router bgp 65001
 bgp router-id {self.ip_address}
 bgp log-neighbor-changes
 neighbor 10.100.0.2 remote-as 65001
 neighbor 10.100.0.2 update-source Loopback0
 !
 address-family ipv4
  network 10.100.0.0 mask 255.255.0.0
  neighbor 10.100.0.2 activate
  neighbor 10.100.0.2 send-community both
 exit-address-family
!
line con 0
 exec-timeout 15 0
 logging synchronous
 stopbits 1
line vty 0 4
 exec-timeout 15 0
 logging synchronous
 transport input ssh
line vty 5 15
 exec-timeout 15 0
 logging synchronous
 transport input ssh
!
end
"""
