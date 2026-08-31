"""
Pydantic schemas for Discovery Scan requests, jobs, and discovered hardware records.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
import ipaddress
from backend.app.discovery.models import JobStatus, ScanType


class DiscoveryScanConfig(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    target_cidr: str = Field(..., description="Target subnet CIDR, e.g. 10.100.0.0/24")
    scan_type: ScanType = ScanType.FULL_DISCOVERY
    snmp_community: Optional[str] = "public"
    ssh_port: int = 22
    concurrency: int = Field(10, ge=1, le=50)

    @field_validator("target_cidr")
    @classmethod
    def validate_cidr(cls, v: str) -> str:
        try:
            ipaddress.ip_network(v, strict=False)
            return v
        except ValueError:
            raise ValueError(f"Invalid CIDR network representation: '{v}'")


class DiscoveredDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    os_detected: Optional[str] = None
    open_ports: List[int] = []
    snmp_responsive: bool
    ssh_responsive: bool
    is_imported: bool
    response_time_ms: Optional[float] = None
    created_at: datetime


class DiscoveryJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    target_cidr: str
    scan_type: ScanType
    status: JobStatus
    progress_percent: int
    discovered_count: int
    failed_count: int
    total_targets: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    discovered_devices: List[DiscoveredDeviceResponse] = []


class ImportDiscoveredRequest(BaseModel):
    device_ids: List[int]
    target_site_id: Optional[int] = None
