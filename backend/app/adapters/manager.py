"""
Adapter manager selecting appropriate physical driver (SNMP/SSH/ICMP) or simulated Lab adapter.
"""

from typing import Optional
from backend.app.config import settings
from backend.app.adapters.base import DeviceAdapter
from backend.app.adapters.icmp_adapter import ICMPAdapter
from backend.app.adapters.snmp_adapter import SNMPAdapter
from backend.app.adapters.ssh_adapter import SSHAdapter
from backend.app.adapters.lab_adapter import LabNetworkAdapter


class AdapterManager:
    @staticmethod
    def get_adapter(
        host_or_ip: str,
        driver: str = "auto",
        username: Optional[str] = None,
        password: Optional[str] = None,
        snmp_community: Optional[str] = "public",
        ssh_port: int = 22,
        force_lab: Optional[bool] = None,
    ) -> DeviceAdapter:
        """Resolve and instantiate the appropriate device adapter."""
        use_lab = settings.LAB_MODE if force_lab is None else force_lab

        if use_lab:
            return LabNetworkAdapter(target_host_or_ip=host_or_ip)

        if driver == "ssh":
            return SSHAdapter(host=host_or_ip, username=username or "admin", password=password, port=ssh_port)
        elif driver == "snmp":
            return SNMPAdapter(host=host_or_ip, community=snmp_community or "public")
        elif driver == "icmp":
            return ICMPAdapter(host=host_or_ip)
        else:
            # Auto fallback: if IP starts with private lab range or lab mode enabled, use lab
            return LabNetworkAdapter(target_host_or_ip=host_or_ip)
