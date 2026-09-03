"""
High-Throughput NetFlow v9 & IPFIX Flow Packet Generator and Anomaly Analyzer.
Simulates high-velocity enterprise traffic records, autonomous system path distribution,
QoS DSCP priority mapping, and TCP flag scan anomaly detection.
"""

from typing import List, Dict, Any, Optional, Tuple
import random
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class FlowPacket:
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    dscp: int
    tcp_flags: int
    bytes_count: int
    packets_count: int
    src_as: int
    dst_as: int
    application: str


class TrafficPacketEngine:
    """NetFlow v9 / IPFIX Packet Generator and TCP Flag Anomaly Engine."""

    DSCP_CLASSES = {
        0: "Best Effort (BE)",
        10: "AF11 (Low Drop - Bulk Data)",
        18: "AF21 (Low Drop - Transactional)",
        26: "AF31 (Low Drop - Streaming Video)",
        34: "AF41 (Low Drop - Video Conferencing)",
        46: "EF (Expedited Forwarding - Voice/VoIP)",
        48: "CS6 (Network Control - OSPF/BGP)",
    }

    @staticmethod
    def generate_flow_batch(count: int = 50) -> List[FlowPacket]:
        """Generate high-fidelity NetFlow v9 flow records."""
        internal_subnets = ["10.100.1.", "10.100.2.", "10.100.3.", "10.200.1."]
        cloud_ips = ["142.250.190.46", "52.216.18.3", "13.107.42.16", "8.8.8.8", "1.1.1.1"]
        apps = [
            ("HTTPS", 443, "TCP", 0),
            ("SSH", 22, "TCP", 18),
            ("DNS", 53, "UDP", 26),
            ("NFS", 2049, "TCP", 10),
            ("BGP", 179, "TCP", 48),
            ("RTP-Voice", 16384, "UDP", 46),
        ]

        flows: List[FlowPacket] = []
        for _ in range(count):
            app_name, port, proto, dscp = random.choice(apps)
            src_ip = random.choice(internal_subnets) + str(random.randint(2, 250))
            dst_ip = random.choice(cloud_ips) if random.random() > 0.4 else random.choice(internal_subnets) + str(random.randint(2, 250))
            
            bytes_n = random.randint(50000, 85000000)
            pkts_n = max(1, bytes_n // random.randint(800, 1500))
            src_as = 65001
            dst_as = random.choice([15169, 16509, 8075, 13335])

            flows.append(
                FlowPacket(
                    src_ip=src_ip,
                    dst_ip=dst_ip,
                    src_port=random.randint(32768, 61000),
                    dst_port=port,
                    protocol=proto,
                    dscp=dscp,
                    tcp_flags=0x18 if proto == "TCP" else 0,  # PSH, ACK
                    bytes_count=bytes_n,
                    packets_count=pkts_n,
                    src_as=src_as,
                    dst_as=dst_as,
                    application=app_name,
                )
            )

        return flows

    @staticmethod
    def analyze_tcp_flag_anomalies(flows: List[FlowPacket]) -> List[Dict[str, Any]]:
        """Detect stealth port scans and TCP flag anomalies."""
        anomalies = []
        for f in flows:
            if f.protocol == "TCP":
                # SYN-FIN scan (0x03)
                if (f.tcp_flags & 0x01) and (f.tcp_flags & 0x02):
                    anomalies.append({
                        "type": "SYN-FIN Scan",
                        "src_ip": f.src_ip,
                        "dst_ip": f.dst_ip,
                        "severity": "HIGH",
                    })
                # NULL scan (0x00)
                elif f.tcp_flags == 0:
                    anomalies.append({
                        "type": "TCP NULL Scan",
                        "src_ip": f.src_ip,
                        "dst_ip": f.dst_ip,
                        "severity": "HIGH",
                    })
                # XMAS scan (0x29 - FIN, PSH, URG)
                elif f.tcp_flags == 0x29:
                    anomalies.append({
                        "type": "TCP XMAS Tree Scan",
                        "src_ip": f.src_ip,
                        "dst_ip": f.dst_ip,
                        "severity": "CRITICAL",
                    })

        return anomalies
