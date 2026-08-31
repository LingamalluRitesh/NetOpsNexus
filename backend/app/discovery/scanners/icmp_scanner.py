"""
High-throughput asynchronous ICMP subnet scanner.
"""

from typing import List, Dict, Any, Tuple
import asyncio
import ipaddress
from backend.app.adapters.manager import AdapterManager
from backend.app.config import settings


class ICMPScanner:
    @staticmethod
    async def scan_target(ip_str: str) -> Tuple[bool, float]:
        """Check reachability and latency for single target IP."""
        adapter = AdapterManager.get_adapter(ip_str)
        try:
            res = await adapter.ping(count=1, timeout_sec=0.8)
            return res.is_reachable, res.avg_rtt_ms
        except Exception:
            return False, 0.0

    @staticmethod
    async def scan_network(cidr: str, concurrency: int = 15) -> List[Dict[str, Any]]:
        """Sweep CIDR block and return list of alive hosts."""
        net = ipaddress.ip_network(cidr, strict=False)
        # Limit scan size to max 256 for rapid interactive scans in demo
        hosts = [str(ip) for ip in list(net.hosts())[:256]]
        semaphore = asyncio.Semaphore(concurrency)
        results = []

        async def worker(ip: str):
            async with semaphore:
                is_alive, rtt = await ICMPScanner.scan_target(ip)
                if is_alive:
                    results.append({"ip": ip, "rtt_ms": rtt})

        tasks = [asyncio.create_task(worker(ip)) for ip in hosts]
        await asyncio.gather(*tasks)
        return results
