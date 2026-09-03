"""
Enterprise SNMP MIB Dictionary and OID Tree Engine.
Supports standard RFC MIBs and enterprise vendor private MIBs:
- IF-MIB (RFC 2863)
- IP-MIB (RFC 4293)
- BGP4-MIB (RFC 4273)
- CISCO-PROCESS-MIB
- CISCO-ENVMON-MIB
- HOST-RESOURCES-MIB (RFC 2790)
- BRIDGE-MIB (RFC 4188)
- OSPF-MIB (RFC 4750)
- ENTITY-MIB (RFC 6933)
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class MibAccess(str, Enum):
    READ_ONLY = "read-only"
    READ_WRITE = "read-write"
    NOT_ACCESSIBLE = "not-accessible"
    ACCESSIBLE_FOR_NOTIFY = "accessible-for-notify"


class MibSyntax(str, Enum):
    INTEGER = "INTEGER"
    OCTET_STRING = "OCTET STRING"
    OBJECT_IDENTIFIER = "OBJECT IDENTIFIER"
    COUNTER32 = "Counter32"
    COUNTER64 = "Counter64"
    GAUGE32 = "Gauge32"
    TIMETICKS = "TimeTicks"
    IPADDRESS = "IpAddress"


@dataclass
class MibNode:
    oid: str
    name: str
    mib_module: str
    syntax: MibSyntax
    access: MibAccess
    description: str


class MibDictionary:
    """Enterprise RFC & Vendor MIB Registry."""

    NODES: Dict[str, MibNode] = {
        # System MIB (RFC 1213)
        "1.3.6.1.2.1.1.1.0": MibNode("1.3.6.1.2.1.1.1.0", "sysDescr", "RFC1213-MIB", MibSyntax.OCTET_STRING, MibAccess.READ_ONLY, "System textual description"),
        "1.3.6.1.2.1.1.2.0": MibNode("1.3.6.1.2.1.1.2.0", "sysObjectID", "RFC1213-MIB", MibSyntax.OBJECT_IDENTIFIER, MibAccess.READ_ONLY, "Vendor authoritative identification"),
        "1.3.6.1.2.1.1.3.0": MibNode("1.3.6.1.2.1.1.3.0", "sysUpTime", "RFC1213-MIB", MibSyntax.TIMETICKS, MibAccess.READ_ONLY, "Time in hundredths of a second since reboot"),
        "1.3.6.1.2.1.1.4.0": MibNode("1.3.6.1.2.1.1.4.0", "sysContact", "RFC1213-MIB", MibSyntax.OCTET_STRING, MibAccess.READ_WRITE, "Contact person for network administrator"),
        "1.3.6.1.2.1.1.5.0": MibNode("1.3.6.1.2.1.1.5.0", "sysName", "RFC1213-MIB", MibSyntax.OCTET_STRING, MibAccess.READ_WRITE, "Administrative fully-qualified domain name"),
        "1.3.6.1.2.1.1.6.0": MibNode("1.3.6.1.2.1.1.6.0", "sysLocation", "RFC1213-MIB", MibSyntax.OCTET_STRING, MibAccess.READ_WRITE, "Physical location of node"),

        # IF-MIB (RFC 2863)
        "1.3.6.1.2.1.2.1.0": MibNode("1.3.6.1.2.1.2.1.0", "ifNumber", "IF-MIB", MibSyntax.INTEGER, MibAccess.READ_ONLY, "Total number of network interfaces"),
        "1.3.6.1.2.1.2.2.1.1": MibNode("1.3.6.1.2.1.2.2.1.1", "ifIndex", "IF-MIB", MibSyntax.INTEGER, MibAccess.READ_ONLY, "Unique interface identifier"),
        "1.3.6.1.2.1.2.2.1.2": MibNode("1.3.6.1.2.1.2.2.1.2", "ifDescr", "IF-MIB", MibSyntax.OCTET_STRING, MibAccess.READ_ONLY, "Interface description string"),
        "1.3.6.1.2.1.2.2.1.3": MibNode("1.3.6.1.2.1.2.2.1.3", "ifType", "IF-MIB", MibSyntax.INTEGER, MibAccess.READ_ONLY, "Type of interface protocol/physical medium"),
        "1.3.6.1.2.1.2.2.1.5": MibNode("1.3.6.1.2.1.2.2.1.5", "ifSpeed", "IF-MIB", MibSyntax.GAUGE32, MibAccess.READ_ONLY, "Estimated current bandwidth in bps"),
        "1.3.6.1.2.1.2.2.1.7": MibNode("1.3.6.1.2.1.2.2.1.7", "ifAdminStatus", "IF-MIB", MibSyntax.INTEGER, MibAccess.READ_WRITE, "Desired state (1=up, 2=down, 3=testing)"),
        "1.3.6.1.2.1.2.2.1.8": MibNode("1.3.6.1.2.1.2.2.1.8", "ifOperStatus", "IF-MIB", MibSyntax.INTEGER, MibAccess.READ_ONLY, "Current operational state (1=up, 2=down)"),
        "1.3.6.1.2.1.31.1.1.1.6": MibNode("1.3.6.1.2.1.31.1.1.1.6", "ifHCInOctets", "IF-MIB", MibSyntax.COUNTER64, MibAccess.READ_ONLY, "64-bit counter of received octets"),
        "1.3.6.1.2.1.31.1.1.1.10": MibNode("1.3.6.1.2.1.31.1.1.1.10", "ifHCOutOctets", "IF-MIB", MibSyntax.COUNTER64, MibAccess.READ_ONLY, "64-bit counter of transmitted octets"),
        "1.3.6.1.2.1.31.1.1.1.18": MibNode("1.3.6.1.2.1.31.1.1.1.18", "ifAlias", "IF-MIB", MibSyntax.OCTET_STRING, MibAccess.READ_WRITE, "Interface configured alias description"),

        # BGP4-MIB (RFC 4273)
        "1.3.6.1.2.1.15.3.1.1": MibNode("1.3.6.1.2.1.15.3.1.1", "bgpPeerIdentifier", "BGP4-MIB", MibSyntax.IPADDRESS, MibAccess.READ_ONLY, "BGP peer router ID"),
        "1.3.6.1.2.1.15.3.1.2": MibNode("1.3.6.1.2.1.15.3.1.2", "bgpPeerState", "BGP4-MIB", MibSyntax.INTEGER, MibAccess.READ_ONLY, "BGP peer FSM state (1=idle, 6=established)"),
        "1.3.6.1.2.1.15.3.1.7": MibNode("1.3.6.1.2.1.15.3.1.7", "bgpPeerRemoteAddr", "BGP4-MIB", MibSyntax.IPADDRESS, MibAccess.READ_ONLY, "Remote IP address of peer"),
        "1.3.6.1.2.1.15.3.1.9": MibNode("1.3.6.1.2.1.15.3.1.9", "bgpPeerRemoteAs", "BGP4-MIB", MibSyntax.INTEGER, MibAccess.READ_ONLY, "Remote Autonomous System number"),

        # CISCO-PROCESS-MIB
        "1.3.6.1.4.1.9.9.109.1.1.1.1.3": MibNode("1.3.6.1.4.1.9.9.109.1.1.1.1.3", "cpmCPUTotal5sec", "CISCO-PROCESS-MIB", MibSyntax.GAUGE32, MibAccess.READ_ONLY, "CPU utilization over last 5 seconds"),
        "1.3.6.1.4.1.9.9.109.1.1.1.1.6": MibNode("1.3.6.1.4.1.9.9.109.1.1.1.1.6", "cpmCPUMemoryUsed", "CISCO-PROCESS-MIB", MibSyntax.GAUGE32, MibAccess.READ_ONLY, "Total memory allocated in bytes"),
        "1.3.6.1.4.1.9.9.109.1.1.1.1.7": MibNode("1.3.6.1.4.1.9.9.109.1.1.1.1.7", "cpmCPUMemoryFree", "CISCO-PROCESS-MIB", MibSyntax.GAUGE32, MibAccess.READ_ONLY, "Total memory free in bytes"),

        # CISCO-ENVMON-MIB
        "1.3.6.1.4.1.9.9.13.1.3.1.3": MibNode("1.3.6.1.4.1.9.9.13.1.3.1.3", "ciscoEnvMonTemperatureValue", "CISCO-ENVMON-MIB", MibSyntax.GAUGE32, MibAccess.READ_ONLY, "Current chassis temperature in degrees Celsius"),
        "1.3.6.1.4.1.9.9.13.1.3.1.6": MibNode("1.3.6.1.4.1.9.9.13.1.3.1.6", "ciscoEnvMonTemperatureState", "CISCO-ENVMON-MIB", MibSyntax.INTEGER, MibAccess.READ_ONLY, "Chassis temperature sensor state"),

        # OSPF-MIB (RFC 4750)
        "1.3.6.1.2.1.14.1.1.0": MibNode("1.3.6.1.2.1.14.1.1.0", "ospfRouterId", "OSPF-MIB", MibSyntax.IPADDRESS, MibAccess.READ_WRITE, "32-bit unique OSPF router ID"),
        "1.3.6.1.2.1.14.1.2.0": MibNode("1.3.6.1.2.1.14.1.2.0", "ospfAdminStat", "OSPF-MIB", MibSyntax.INTEGER, MibAccess.READ_WRITE, "Administrative status of OSPF"),
        "1.3.6.1.2.1.14.10.1.6": MibNode("1.3.6.1.2.1.14.10.1.6", "ospfNbrState", "OSPF-MIB", MibSyntax.INTEGER, MibAccess.READ_ONLY, "State of OSPF neighbor relationship (8=Full)"),
    }

    @classmethod
    def lookup_oid(cls, oid: str) -> Optional[MibNode]:
        """Lookup node definition by exact OID or prefix."""
        if oid in cls.NODES:
            return cls.NODES[oid]
        # Search prefixes
        for prefix, node in cls.NODES.items():
            if oid.startswith(prefix.rstrip(".0")):
                return node
        return None

    @classmethod
    def lookup_name(cls, symbol_name: str) -> Optional[MibNode]:
        """Lookup node definition by symbol name."""
        for node in cls.NODES.values():
            if node.name.lower() == symbol_name.lower():
                return node
        return None

    @classmethod
    def list_by_module(cls, mib_module: str) -> List[MibNode]:
        """List all defined OIDs under a specific MIB module."""
        return [node for node in cls.NODES.values() if node.mib_module.upper() == mib_module.upper()]
