"""
ICMP Ping driver using native socket and asyncio subprocess execution.
"""

import asyncio
import re
import platform
import time
from typing import Optional
from backend.app.adapters.base import AdapterPingResult


class ICMPAdapter:
    def __init__(self, host: str):
        self.host = host

    async def ping(self, count: int = 5, timeout_sec: float = 2.0, packet_size: int = 56) -> AdapterPingResult:
        """Execute ICMP ping sweep and compute RTT statistics and packet loss."""
        start_time = time.time()
        is_windows = platform.system().lower() == "windows"

        if is_windows:
            cmd = ["ping", "-n", str(count), "-w", str(int(timeout_sec * 1000)), "-l", str(packet_size), self.host]
        else:
            cmd = ["ping", "-c", str(count), "-W", str(int(timeout_sec)), "-s", str(packet_size), self.host]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout_sec * count + 5.0)
            output = stdout.decode("utf-8", errors="ignore")
            
            # Parse output
            if is_windows:
                # Windows ping parsing
                received_match = re.search(r"Received = (\d+)", output)
                lost_match = re.search(r"Lost = (\d+)", output)
                min_match = re.search(r"Minimum = (\d+)ms", output)
                max_match = re.search(r"Maximum = (\d+)ms", output)
                avg_match = re.search(r"Average = (\d+)ms", output)

                received = int(received_match.group(1)) if received_match else 0
                lost = int(lost_match.group(1)) if lost_match else count
                loss_pct = (lost / count) * 100.0 if count > 0 else 100.0

                min_rtt = float(min_match.group(1)) if min_match else 0.0
                max_rtt = float(max_match.group(1)) if max_match else 0.0
                avg_rtt = float(avg_match.group(1)) if avg_match else 0.0
            else:
                # Unix ping parsing
                rec_match = re.search(r"(\d+) packets transmitted, (\d+) received", output)
                rtt_match = re.search(r"rtt min/avg/max/mdev = ([\d\.]+)/([\d\.]+)/([\d\.]+)/([\d\.]+)", output)
                
                received = int(rec_match.group(2)) if rec_match else 0
                loss_pct = ((count - received) / count) * 100.0 if count > 0 else 100.0
                
                if rtt_match:
                    min_rtt = float(rtt_match.group(1))
                    avg_rtt = float(rtt_match.group(2))
                    max_rtt = float(rtt_match.group(3))
                    stddev = float(rtt_match.group(4))
                else:
                    min_rtt, avg_rtt, max_rtt, stddev = 0.0, 0.0, 0.0, 0.0

            return AdapterPingResult(
                target=self.host,
                packets_transmitted=count,
                packets_received=received,
                packet_loss_percent=loss_pct,
                min_rtt_ms=min_rtt,
                avg_rtt_ms=avg_rtt,
                max_rtt_ms=max_rtt,
                stddev_rtt_ms=0.0,
                is_reachable=received > 0,
            )
        except Exception:
            return AdapterPingResult(
                target=self.host,
                packets_transmitted=count,
                packets_received=0,
                packet_loss_percent=100.0,
                min_rtt_ms=0.0,
                avg_rtt_ms=0.0,
                max_rtt_ms=0.0,
                stddev_rtt_ms=0.0,
                is_reachable=False,
            )
