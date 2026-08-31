"""
Pydantic schemas for Devices, Interfaces, Routes, Sites, Racks, and VLANs.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from backend.app.devices.models import (
    DeviceType, DeviceStatus, InterfaceAdminStatus, InterfaceOperStatus, RouteProtocol
)


# --- Site & Rack Schemas ---
class SiteBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    code: str = Field(..., min_length=2, max_length=32)
    address: Optional[str] = None
    city: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_email: Optional[str] = None


class SiteCreate(SiteBase):
    pass


class SiteResponse(SiteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class RackBase(BaseModel):
    site_id: int
    name: str
    unit_height: int = 42
    location_row: Optional[str] = None


class RackCreate(RackBase):
    pass


class RackResponse(RackBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# --- Interface Schemas ---
class InterfaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    subnet_mask: Optional[str] = None
    speed_mbps: int = 1000
    duplex: str = "full"
    mtu: int = 1500
    admin_status: InterfaceAdminStatus = InterfaceAdminStatus.UP
    oper_status: InterfaceOperStatus = InterfaceOperStatus.UP
    vlan_id: Optional[int] = None
    is_trunk: bool = False
    is_management: bool = False


class InterfaceCreate(InterfaceBase):
    device_id: int


class InterfaceUpdate(BaseModel):
    description: Optional[str] = None
    ip_address: Optional[str] = None
    subnet_mask: Optional[str] = None
    admin_status: Optional[InterfaceAdminStatus] = None
    oper_status: Optional[InterfaceOperStatus] = None
    vlan_id: Optional[int] = None
    speed_mbps: Optional[int] = None


class InterfaceResponse(InterfaceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    rx_bps: float
    tx_bps: float
    rx_pps: float
    tx_pps: float
    rx_errors: int
    tx_errors: int
    rx_drops: int
    tx_drops: int
    last_change: Optional[datetime] = None


# --- Route Schemas ---
class RouteBase(BaseModel):
    destination_prefix: str
    next_hop: str
    protocol: RouteProtocol = RouteProtocol.STATIC
    metric: int = 1
    admin_distance: int = 1
    outgoing_interface: Optional[str] = None
    is_active: bool = True
    age_seconds: int = 0


class RouteCreate(RouteBase):
    device_id: int


class RouteResponse(RouteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int


# --- VLAN Schemas ---
class VlanBase(BaseModel):
    vlan_id: int
    name: str
    description: Optional[str] = None
    site_id: Optional[int] = None
    status: str = "active"


class VlanCreate(VlanBase):
    pass


class VlanResponse(VlanBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# --- Device Schemas ---
class DeviceBase(BaseModel):
    hostname: str = Field(..., min_length=2, max_length=128)
    management_ip: str
    device_type: DeviceType = DeviceType.ACCESS_SWITCH
    vendor: str
    model: str
    os_type: str = "cisco_ios"
    os_version: str = "17.9.4"
    serial_number: Optional[str] = None
    mac_address: Optional[str] = None
    site_id: Optional[int] = None
    rack_id: Optional[int] = None
    rack_unit: Optional[int] = None
    status: DeviceStatus = DeviceStatus.ONLINE
    snmp_community: Optional[str] = "public"
    snmp_version: str = "2c"
    ssh_port: int = 22
    is_managed: bool = True
    tags: Optional[Dict[str, Any]] = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    hostname: Optional[str] = None
    management_ip: Optional[str] = None
    device_type: Optional[DeviceType] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    os_type: Optional[str] = None
    os_version: Optional[str] = None
    site_id: Optional[int] = None
    rack_id: Optional[int] = None
    rack_unit: Optional[int] = None
    status: Optional[DeviceStatus] = None
    snmp_community: Optional[str] = None
    ssh_port: Optional[int] = None
    is_managed: Optional[bool] = None
    tags: Optional[Dict[str, Any]] = None


class DeviceResponse(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uptime_seconds: int
    cpu_utilization: float
    memory_utilization: float
    temperature_celsius: Optional[float] = None
    last_seen: datetime
    created_at: datetime
    updated_at: datetime
    site: Optional[SiteResponse] = None
    interfaces: List[InterfaceResponse] = []
    routes: List[RouteResponse] = []


class DeviceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hostname: str
    management_ip: str
    device_type: DeviceType
    vendor: str
    model: str
    status: DeviceStatus
    site_name: Optional[str] = None
    cpu_utilization: float
    memory_utilization: float
    interface_count: int = 0
    last_seen: datetime


class DeviceCliCommandRequest(BaseModel):
    command: str = Field(..., min_length=1)
    timeout_seconds: int = 10


class DeviceCliCommandResponse(BaseModel):
    device_id: int
    hostname: str
    command: str
    output: str
    execution_time_ms: float
    status: str
