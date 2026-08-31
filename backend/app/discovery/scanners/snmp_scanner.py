"""
SNMP device fingerprinting and system identification scanner.
"""

from typing import Dict, Any, Optional
from backend.app.adapters.manager import AdapterManager


class SNMPScanner:
    @staticmethod
    async def fingerprint_device(ip: str, community: str = "public") -> Dict[str, Any]:
        """Query system MIB parameters to identify vendor, model, OS, and MAC."""
        adapter = AdapterManager.get_adapter(ip, snmp_community=community)
        try:
            sys_info = await adapter.get_system_info()
            return {
                "responsive": True,
                "hostname": sys_info.hostname,
                "vendor": sys_info.vendor,
                "model": sys_info.model,
                "os_detected": f"{sys_info.os_type} {sys_info.os_version}",
                "mac_address": sys_info.mac_address,
            }
        except Exception:
            return {
                "responsive": False,
                "hostname": None,
                "vendor": "Unknown",
                "model": "Unknown",
                "os_detected": "Unknown",
                "mac_address": None,
            }
