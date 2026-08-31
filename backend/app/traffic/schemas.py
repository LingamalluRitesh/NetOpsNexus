"""
Pydantic schemas for NetFlow / sFlow Ingestion, Top Talkers, and Traffic Analytics.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class FlowRecordCreate(BaseModel):
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str = "TCP"
    bytes_count: int
    packets_count: int
    application_name: Optional[str] = "HTTPS"
    device_id: Optional[int] = None
    interface_id: Optional[int] = None


class FlowRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    bytes_count: int
    packets_count: int
    application_name: str
    device_id: Optional[int] = None


class TopTalkerItem(BaseModel):
    entity: str  # IP address or Application
    bytes_total: int
    megabytes_total: float
    percentage: float
    flows_count: int


class TopTalkersResponse(BaseModel):
    time_window_hours: int
    total_volume_gigabytes: float
    top_sources: List[TopTalkerItem]
    top_destinations: List[TopTalkerItem]
    top_applications: List[TopTalkerItem]
    top_protocols: List[TopTalkerItem]
