"""
Pydantic schemas for Network Diagnostics Toolkit (Ping, Traceroute, DNS, Port Probe, Path Analysis).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PingRequest(BaseModel):
    source_device_id: Optional[int] = None
    target: str = Field(..., description="Target hostname or IP address")
    count: int = Field(4, ge=1, le=20)
    packet_size: int = Field(64, ge=32, le=1500)
    timeout_sec: float = Field(1.5, ge=0.5, le=10.0)


class PingResponse(BaseModel):
    target: str
    is_reachable: bool
    packets_sent: int
    packets_received: int
    packet_loss_percent: float
    min_rtt_ms: float
    avg_rtt_ms: float
    max_rtt_ms: float
    rtt_samples: List[float]
    executed_at: datetime


class TracerouteRequest(BaseModel):
    source_device_id: Optional[int] = None
    target: str = Field(..., description="Target destination IP or hostname")
    max_hops: int = Field(15, ge=1, le=30)
    timeout_sec: float = Field(2.0, ge=0.5, le=5.0)


class TraceHop(BaseModel):
    hop_number: int
    ip_address: str
    hostname: Optional[str] = None
    rtt_ms: float
    status: str  # responding, timeout, filtered


class TracerouteResponse(BaseModel):
    target: str
    total_hops: int
    is_completed: bool
    hops: List[TraceHop]
    executed_at: datetime


class DnsLookupRequest(BaseModel):
    query_name: str
    record_type: str = "A"  # A, AAAA, CNAME, MX, TXT, PTR
    dns_server: Optional[str] = "8.8.8.8"


class DnsLookupResponse(BaseModel):
    query_name: str
    record_type: str
    dns_server: str
    answers: List[str]
    response_time_ms: float
    status: str


class PortProbeRequest(BaseModel):
    target_ip: str
    port: int = Field(..., ge=1, le=65535)
    protocol: str = "TCP"  # TCP or UDP
    timeout_sec: float = 2.0


class PortProbeResponse(BaseModel):
    target_ip: str
    port: int
    protocol: str
    is_open: bool
    service_name: Optional[str] = None
    banner: Optional[str] = None
    latency_ms: float
