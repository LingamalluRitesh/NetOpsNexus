"""
Pydantic schemas for IPAM Subnets, IP allocation, CIDR calculator, and Conflicts.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
import ipaddress
from backend.app.ipam.models import SubnetStatus, IpStatus


class VrfBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=64)
    rd: Optional[str] = None
    description: Optional[str] = None
    is_default: bool = False


class VrfCreate(VrfBase):
    pass


class VrfResponse(VrfBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SubnetBase(BaseModel):
    network_address: str
    prefix_len: int = Field(..., ge=1, le=128)
    ip_version: int = Field(4, ge=4, le=6)
    vrf_id: Optional[int] = None
    site_id: Optional[int] = None
    vlan_id: Optional[int] = None
    name: str = Field(..., min_length=2, max_length=128)
    description: Optional[str] = None
    gateway_ip: Optional[str] = None
    status: SubnetStatus = SubnetStatus.ACTIVE


class SubnetCreate(SubnetBase):
    @field_validator("network_address")
    @classmethod
    def validate_net(cls, v: str) -> str:
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid IP address format: '{v}'")


class SubnetResponse(SubnetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    total_ips: int
    used_ips: int
    reserved_ips: int
    available_ips: int = 0
    utilization_pct: float = 0.0
    created_at: datetime


class IpAddressBase(BaseModel):
    subnet_id: int
    address: str
    status: IpStatus = IpStatus.ALLOCATED
    fqdn: Optional[str] = None
    mac_address: Optional[str] = None
    device_id: Optional[int] = None
    interface_id: Optional[int] = None
    description: Optional[str] = None
    is_dhcp: bool = False
    allocated_to: Optional[str] = None


class IpAddressCreate(IpAddressBase):
    pass


class IpAddressResponse(IpAddressBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    last_seen: datetime
    created_at: datetime


class SubnetSplitRequest(BaseModel):
    subnet_id: int
    new_prefix_len: int = Field(..., description="Target prefix length to split into, e.g. /25 from /24")


class SubnetMergeRequest(BaseModel):
    subnet_ids: List[int] = Field(..., min_length=2)


class CidrCalculationRequest(BaseModel):
    cidr: str = Field(..., description="e.g. 10.20.10.0/24")


class CidrCalculationResponse(BaseModel):
    cidr: str
    network_address: str
    broadcast_address: str
    netmask: str
    wildcard_mask: str
    prefix_len: int
    ip_version: int
    total_addresses: int
    usable_hosts: int
    first_usable_ip: str
    last_usable_ip: str
    is_private: bool


class IpConflictResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ip_address: str
    subnet_id: int
    conflicting_macs: List[str]
    conflicting_device_ids: List[int]
    detected_at: datetime
    is_resolved: bool
    resolution_notes: Optional[str] = None
