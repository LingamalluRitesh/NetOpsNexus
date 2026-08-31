"""
Pydantic schemas for Telemetry time-series data, live streams, and monitoring dashboards.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float


class DeviceMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    timestamp: datetime
    cpu_utilization: float
    memory_utilization: float
    temperature_celsius: Optional[float] = None
    uptime_seconds: int
    is_reachable: bool
    latency_ms: float
    packet_loss_pct: float


class InterfaceMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    interface_id: int
    timestamp: datetime
    rx_bps: float
    tx_bps: float
    rx_pps: float
    tx_pps: float
    rx_errors: int
    tx_errors: int
    rx_drops: int
    tx_drops: int
    utilization_pct: float


class DeviceTelemetryHistory(BaseModel):
    device_id: int
    hostname: str
    cpu_series: List[TimeSeriesPoint]
    memory_series: List[TimeSeriesPoint]
    latency_series: List[TimeSeriesPoint]
    packet_loss_series: List[TimeSeriesPoint]
    avg_cpu: float
    max_cpu: float
    p95_cpu: float
    current_status: str


class InterfaceTelemetryHistory(BaseModel):
    interface_id: int
    interface_name: str
    rx_bps_series: List[TimeSeriesPoint]
    tx_bps_series: List[TimeSeriesPoint]
    utilization_series: List[TimeSeriesPoint]
    errors_total: int
    drops_total: int
    peak_rx_mbps: float
    peak_tx_mbps: float


class MonitoringOverviewResponse(BaseModel):
    total_devices_monitored: int
    devices_online: int
    devices_warning: int
    devices_critical: int
    average_network_cpu: float
    average_network_memory: float
    average_latency_ms: float
    total_throughput_gbps: float
    total_packet_errors_1h: int
    top_utilized_interfaces: List[Dict[str, Any]]
    active_bgp_sessions: int
