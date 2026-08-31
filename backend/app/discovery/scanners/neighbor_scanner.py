"""
LLDP/CDP and ARP neighbor relationship scanner.
"""

from typing import List, Dict, Any
from backend.app.adapters.manager import AdapterManager


class NeighborScanner:
    @staticmethod
    async def discover_neighbors(ip: str) -> List[Dict[str, Any]]:
        """Query LLDP/CDP neighbor tables from device adapter."""
        adapter = AdapterManager.get_adapter(ip)
        try:
            neighbors = await adapter.get_neighbors()
            return [
                {
                    "local_interface": n.local_interface,
                    "neighbor_hostname": n.neighbor_hostname,
                    "neighbor_interface": n.neighbor_interface,
                    "neighbor_ip": n.neighbor_ip,
                    "protocol": n.protocol,
                }
                for n in neighbors
            ]
        except Exception:
            return []
