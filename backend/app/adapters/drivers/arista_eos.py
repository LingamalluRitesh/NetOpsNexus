"""
Arista EOS Network Operating System Driver.
Provides authentic eAPI JSON-RPC / CLI parsing, BGP EVPN / VXLAN configurations,
interface status tables, and running-config diff representations.
"""

from typing import Dict, Any, List, Optional
import time


class AristaEosDriver:
    VENDOR = "Arista Networks"
    OS_NAME = "Arista EOS"
    DEFAULT_PORT = 22

    def __init__(self, hostname: str, ip_address: str, version: str = "4.30.2F"):
        self.hostname = hostname
        self.ip_address = ip_address
        self.version = version
        self.uptime_seconds = 4120000

    def generate_banner(self) -> str:
        return f"""
===============================================================================
  Arista Networks EOS Command Line Interface
  Hostname: {self.hostname:<15}  Model: DCS-7050SX3-48YC8
  Software Version: {self.version}  Management IP: {self.ip_address}
===============================================================================
"""

    def parse_show_version(self) -> Dict[str, Any]:
        return {
            "vendor": self.VENDOR,
            "os_name": self.OS_NAME,
            "version": self.version,
            "hostname": self.hostname,
            "model_name": "DCS-7050SX3-48YC8",
            "internal_version": "4.30.2F-32895821.4302F",
            "system_mac": f"50:08:00:{abs(hash(self.hostname)) % 256:02x}:12:34",
            "serial_number": f"JPE{abs(hash(self.hostname)) % 10000000:07d}",
            "uptime_seconds": self.uptime_seconds,
            "total_memory_kb": 32882104,
            "free_memory_kb": 24982190,
        }

    def parse_show_interfaces_status(self, interfaces: List[Dict[str, Any]]) -> str:
        lines = [
            f"Port       Name                     Status       Vlan     Duplex Speed  Type            Flags",
            f"---------------------------------------------------------------------------------------------",
        ]
        for iface in interfaces:
            port = iface.get("name", "Ethernet1/1").replace("HundredGigE", "Et").replace("GigabitEthernet", "Et")
            descr = iface.get("description", "Uplink to Spine")[:24]
            status = "connected" if iface.get("oper_status") == "up" else "notconnect"
            vlan = "routed"
            speed = "100G" if "100" in str(iface.get("speed_mbps", 100000)) else "10G"
            lines.append(f"{port:<10} {descr:<24} {status:<12} {vlan:<8} full   {speed:<6} 100GBASE-CR4   ")
        return "\n".join(lines)

    def parse_show_ip_bgp_summary(self, local_as: int, peers: List[Dict[str, Any]]) -> str:
        lines = [
            f"BGP summary information for VRF default",
            f"Router identifier {self.ip_address}, local AS number {local_as}",
            f"Neighbor Status Codes: m - Under maintenance",
            f"  Neighbor         V  AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc",
            f"------------------------------------------------------------------------------------------------",
        ]
        for p in peers:
            nbr = p.get("neighbor_ip", "10.200.0.1")
            as_num = p.get("remote_as", 65001)
            rcvd = p.get("msg_rcvd", 12890)
            sent = p.get("msg_sent", 12895)
            uptime = p.get("uptime", "3d14h")
            pfx = p.get("prefixes_received", 38)
            lines.append(f"  {nbr:<16} 4  {as_num:<12} {rcvd:<9} {sent:<8}    0    0 {uptime:<7} Estab   {pfx:<6} {pfx:<6}")
        return "\n".join(lines)

    def parse_show_running_config(self) -> str:
        return f"""! Command: show running-config
! device: {self.hostname} (DCS-7050SX3-48YC8, EOS-{self.version})
!
! boot system flash:/EOS-{self.version}.swi
!
transceiver qsfp default-mode 4x10G
!
service routing protocols model multi-agent
!
hostname {self.hostname}
ip domain lookup vrf MGMT
ip name-server vrf MGMT 10.100.1.1
!
spanning-tree mode mstp
!
vrf instance MGMT
!
management api http-commands
   no shutdown
   vrf MGMT
      no shutdown
!
interface Ethernet1/1
   description Spine-01_Leaf-Interconnect
   mtu 9214
   no switchport
   ip address 10.100.0.9/30
!
interface Ethernet1/2
   description Spine-02_Leaf-Interconnect
   mtu 9214
   no switchport
   ip address 10.100.0.13/30
!
interface Loopback0
   description EVPN-VTEP-Loopback
   ip address {self.ip_address}/32
!
interface Vxlan1
   vxlan source-interface Loopback0
   vxlan udp-port 4789
   vxlan vlan 100 vni 10100
   vxlan vlan 200 vni 10200
!
ip routing
ip routing vrf MGMT
!
router bgp 65002
   router-id {self.ip_address}
   neighbor EVPN-OVERLAY-PEERS peer group
   neighbor EVPN-OVERLAY-PEERS remote-as 65001
   neighbor EVPN-OVERLAY-PEERS update-source Loopback0
   neighbor EVPN-OVERLAY-PEERS send-community
   neighbor 10.100.0.10 peer group EVPN-OVERLAY-PEERS
   neighbor 10.100.0.14 peer group EVPN-OVERLAY-PEERS
   !
   address-family evpn
      neighbor EVPN-OVERLAY-PEERS activate
   !
   address-family ipv4
      network 10.100.0.0/24
!
end
"""
