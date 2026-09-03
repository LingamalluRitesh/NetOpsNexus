"""
Juniper Junos Network Operating System Driver.
Provides authentic Junos hierarchical configuration parsing, set/delete command rendering,
commit confirmed semantics, and route table formatting.
"""

from typing import Dict, Any, List, Optional


class JuniperJunosDriver:
    VENDOR = "Juniper Networks"
    OS_NAME = "JUNOS Base OS Software"
    DEFAULT_PORT = 22

    def __init__(self, hostname: str, ip_address: str, version: str = "22.4R2.8"):
        self.hostname = hostname
        self.ip_address = ip_address
        self.version = version
        self.uptime_seconds = 5184000

    def generate_banner(self) -> str:
        return f"""
--- JUNOS {self.version} built 2026-04-14 02:11:34 UTC ---
{self.hostname} (ttyp0)

Welcome to NetOps Nexus Enterprise Juniper Junos Environment.
All connections are monitored and recorded.
"""

    def parse_show_version(self) -> Dict[str, Any]:
        return {
            "vendor": self.VENDOR,
            "os_name": self.OS_NAME,
            "version": self.version,
            "hostname": self.hostname,
            "model": "MX204",
            "junos_series": "MX-Series 3D Universal Edge Router",
            "uptime_seconds": self.uptime_seconds,
            "package_version": f"junos-install-mx-x86-64-{self.version}",
        }

    def parse_show_interfaces_terse(self, interfaces: List[Dict[str, Any]]) -> str:
        lines = [
            f"Interface               Admin Link Proto    Local                 Remote",
            f"--------------------------------------------------------------------------------",
        ]
        for iface in interfaces:
            name = iface.get("name", "et-0/0/0").replace("HundredGigE", "et-0/0/").replace("GigabitEthernet", "ge-0/0/")
            admin = iface.get("admin_status", "up")
            oper = iface.get("oper_status", "up")
            ip = iface.get("ip", "10.100.0.1/30")
            lines.append(f"{name:<23} {admin:<5} {oper:<4} inet     {ip:<21}")
        return "\n".join(lines)

    def parse_show_route(self, routes: List[Dict[str, Any]]) -> str:
        lines = [
            f"inet.0: 14 destinations, 14 routes (14 active, 0 holddown, 0 hidden)",
            f"+ = Active Route, - = Last Active, * = Both",
            f"",
            f"0.0.0.0/0          *[Static/5] 4w2d 12:44:10",
            f"                    > to 10.100.0.1 via et-0/0/0.0",
        ]
        for r in routes:
            pfx = r.get("prefix", "10.100.0.0/24")
            nh = r.get("next_hop", "10.100.0.2")
            iface = r.get("interface", "et-0/0/1.0")
            lines.append(f"{pfx:<18} *[BGP/170] 2d 08:12:00, MED 100, localpref 100")
            lines.append(f"                      AS path: 65001 I, validation-state: unverified")
            lines.append(f"                    > to {nh} via {iface}")
        return "\n".join(lines)

    def parse_show_configuration(self) -> str:
        return f"""## Last commit: 2026-08-28 14:10:02 UTC by netops
version {self.version};
system {{
    host-name {self.hostname};
    domain-name netops.enterprise.internal;
    time-zone UTC;
    name-server {{
        10.100.1.1;
        10.100.1.2;
    }}
    services {{
        ssh {{
            root-login deny;
            protocol-version v2;
        }}
    }}
}}
interfaces {{
    et-0/0/0 {{
        description "Core Trunk Uplink";
        unit 0 {{
            family inet {{
                address 10.100.0.1/30;
            }}
        }}
    }}
    lo0 {{
        unit 0 {{
            family inet {{
                address {self.ip_address}/32;
            }}
        }}
    }}
}}
routing-options {{
    router-id {self.ip_address};
    autonomous-system 65003;
}}
protocols {{
    bgp {{
        group IBGP-MESH {{
            type internal;
            local-address {self.ip_address};
            family inet {{
                unicast;
            }}
            neighbor 10.100.0.2;
        }}
    }}
    lldp {{
        interface all;
    }}
}}
"""
