"""
Pydantic schemas for Topology Graph, Path Tracing, Dependency Mapping, and SPOF analysis.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from backend.app.topology.models import LinkType, LinkStatus
from backend.app.devices.models import DeviceType, DeviceStatus


class TopologyNodeResponse(BaseModel):
    id: str  # e.g., "dev-1"
    device_id: int
    hostname: str
    management_ip: str
    device_type: DeviceType
    vendor: str
    model: str
    status: DeviceStatus
    site_id: Optional[int] = None
    site_name: Optional[str] = None
    cpu_utilization: float
    memory_utilization: float
    interface_count: int
    x: Optional[float] = None
    y: Optional[float] = None


class TopologyEdgeResponse(BaseModel):
    id: str  # e.g., "link-1"
    link_id: int
    source: str  # source node id
    target: str  # target node id
    source_device_id: int
    target_device_id: int
    source_interface_name: Optional[str] = None
    target_interface_name: Optional[str] = None
    link_type: LinkType
    bandwidth_mbps: int
    latency_ms: float
    packet_loss_pct: float
    utilization_pct: float
    status: LinkStatus


class TopologyGraphResponse(BaseModel):
    nodes: List[TopologyNodeResponse]
    edges: List[TopologyEdgeResponse]
    total_nodes: int
    total_edges: int
    healthy_links: int
    degraded_links: int
    down_links: int


class PathTraceRequest(BaseModel):
    source_device_id: int
    target_device_id: int
    optimize_for: str = "latency"  # latency, bandwidth, hops


class PathHop(BaseModel):
    hop_number: int
    device_id: int
    hostname: str
    management_ip: str
    device_type: str
    ingress_interface: Optional[str] = None
    egress_interface: Optional[str] = None
    link_latency_ms: float
    link_loss_pct: float
    link_utilization_pct: float


class PathTraceResponse(BaseModel):
    source_hostname: str
    target_hostname: str
    is_path_found: bool
    total_hops: int
    total_latency_ms: float
    accumulated_loss_pct: float
    min_bottleneck_bandwidth_mbps: int
    primary_path: List[PathHop]
    redundant_paths: List[List[PathHop]] = []


class DependencyAnalysisResponse(BaseModel):
    target_device_id: int
    hostname: str
    upstream_dependencies: List[TopologyNodeResponse]
    downstream_impact: List[TopologyNodeResponse]
    affected_site_ids: List[int]
    blast_radius_device_count: int
    is_single_point_of_failure: bool
    impact_severity: str  # critical, high, medium, low


class SpofReportResponse(BaseModel):
    single_points_of_failure: List[TopologyNodeResponse]
    critical_bridge_links: List[TopologyEdgeResponse]
    network_connectivity_score: float


class LayoutSaveRequest(BaseModel):
    name: str = "default"
    site_id: Optional[int] = None
    node_positions: Dict[str, Dict[str, float]]  # {"dev-1": {"x": 100, "y": 200}}
