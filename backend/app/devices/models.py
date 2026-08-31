"""
SQLAlchemy ORM models for Sites, Racks, Devices, Interfaces, Routing Tables, and VLANs.
"""

from typing import List, Optional
from sqlalchemy import String, Integer, BigInteger, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import enum
from backend.app.database import Base


class DeviceType(str, enum.Enum):
    CORE_ROUTER = "core_router"
    EDGE_ROUTER = "edge_router"
    SPINE_SWITCH = "spine_switch"
    LEAF_SWITCH = "leaf_switch"
    DISTRIBUTION_SWITCH = "distribution_switch"
    ACCESS_SWITCH = "access_switch"
    FIREWALL = "firewall"
    LOAD_BALANCER = "load_balancer"
    WIRELESS_AP = "wireless_ap"
    SERVER = "server"
    GATEWAY = "gateway"


class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class InterfaceOperStatus(str, enum.Enum):
    UP = "up"
    DOWN = "down"
    TESTING = "testing"
    UNKNOWN = "unknown"
    DORMANT = "dormant"
    NOT_PRESENT = "not_present"
    LOWER_LAYER_DOWN = "lower_layer_down"


class InterfaceAdminStatus(str, enum.Enum):
    UP = "up"
    DOWN = "down"
    TESTING = "testing"


class RouteProtocol(str, enum.Enum):
    DIRECT = "direct"
    STATIC = "static"
    BGP = "bgp"
    OSPF = "ospf"
    ISIS = "isis"
    RIP = "rip"


class Site(Base):
    __tablename__ = "sites"

    name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(64), nullable=False)
    country: Mapped[str] = mapped_column(String(64), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    # Relationships
    racks: Mapped[List["Rack"]] = relationship("Rack", back_populates="site", cascade="all, delete-orphan", lazy="selectin")
    devices: Mapped[List["Device"]] = relationship("Device", back_populates="site", lazy="selectin")
    vlans: Mapped[List["Vlan"]] = relationship("Vlan", back_populates="site", lazy="selectin")


class Rack(Base):
    __tablename__ = "racks"

    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    unit_height: Mapped[int] = mapped_column(Integer, default=42)
    location_row: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    site: Mapped["Site"] = relationship("Site", back_populates="racks")
    devices: Mapped[List["Device"]] = relationship("Device", back_populates="rack", lazy="selectin")


class Device(Base):
    __tablename__ = "devices"

    hostname: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    management_ip: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(SQLEnum(DeviceType), default=DeviceType.ACCESS_SWITCH, index=True)
    vendor: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    os_type: Mapped[str] = mapped_column(String(64), nullable=False)  # cisco_ios, cisco_nxos, arista_eos, juniper_junos, panos
    os_version: Mapped[str] = mapped_column(String(64), nullable=False)
    serial_number: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    
    site_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True)
    rack_id: Mapped[Optional[int]] = mapped_column(ForeignKey("racks.id", ondelete="SET NULL"), nullable=True, index=True)
    rack_unit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    status: Mapped[DeviceStatus] = mapped_column(SQLEnum(DeviceStatus), default=DeviceStatus.ONLINE, index=True)
    uptime_seconds: Mapped[int] = mapped_column(BigInteger, default=0)
    cpu_utilization: Mapped[float] = mapped_column(Float, default=0.0)
    memory_utilization: Mapped[float] = mapped_column(Float, default=0.0)
    temperature_celsius: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    snmp_community: Mapped[Optional[str]] = mapped_column(String(64), default="public")
    snmp_version: Mapped[str] = mapped_column(String(16), default="2c")
    ssh_port: Mapped[int] = mapped_column(Integer, default=22)
    is_managed: Mapped[bool] = mapped_column(Boolean, default=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    site: Mapped[Optional["Site"]] = relationship("Site", back_populates="devices")
    rack: Mapped[Optional["Rack"]] = relationship("Rack", back_populates="devices")
    interfaces: Mapped[List["NetworkInterface"]] = relationship("NetworkInterface", back_populates="device", cascade="all, delete-orphan", lazy="selectin")
    routes: Mapped[List["RoutingTableEntry"]] = relationship("RoutingTableEntry", back_populates="device", cascade="all, delete-orphan", lazy="selectin")


class NetworkInterface(Base):
    __tablename__ = "network_interfaces"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    if_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    subnet_mask: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    speed_mbps: Mapped[int] = mapped_column(BigInteger, default=1000)
    duplex: Mapped[str] = mapped_column(String(16), default="full")  # full, half, auto
    mtu: Mapped[int] = mapped_column(Integer, default=1500)
    
    admin_status: Mapped[InterfaceAdminStatus] = mapped_column(SQLEnum(InterfaceAdminStatus), default=InterfaceAdminStatus.UP)
    oper_status: Mapped[InterfaceOperStatus] = mapped_column(SQLEnum(InterfaceOperStatus), default=InterfaceOperStatus.UP)
    
    vlan_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_trunk: Mapped[bool] = mapped_column(Boolean, default=False)
    is_management: Mapped[bool] = mapped_column(Boolean, default=False)

    # Live Traffic Counters
    rx_bps: Mapped[float] = mapped_column(Float, default=0.0)
    tx_bps: Mapped[float] = mapped_column(Float, default=0.0)
    rx_pps: Mapped[float] = mapped_column(Float, default=0.0)
    tx_pps: Mapped[float] = mapped_column(Float, default=0.0)
    rx_errors: Mapped[int] = mapped_column(BigInteger, default=0)
    tx_errors: Mapped[int] = mapped_column(BigInteger, default=0)
    rx_drops: Mapped[int] = mapped_column(BigInteger, default=0)
    tx_drops: Mapped[int] = mapped_column(BigInteger, default=0)
    last_change: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    device: Mapped["Device"] = relationship("Device", back_populates="interfaces")


class RoutingTableEntry(Base):
    __tablename__ = "routing_table_entries"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_prefix: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    next_hop: Mapped[str] = mapped_column(String(64), nullable=False)
    protocol: Mapped[RouteProtocol] = mapped_column(SQLEnum(RouteProtocol), default=RouteProtocol.STATIC, index=True)
    metric: Mapped[int] = mapped_column(Integer, default=1)
    admin_distance: Mapped[int] = mapped_column(Integer, default=1)
    outgoing_interface: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    age_seconds: Mapped[int] = mapped_column(Integer, default=0)

    device: Mapped["Device"] = relationship("Device", back_populates="routes")


class Vlan(Base):
    __tablename__ = "vlans"

    vlan_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    site_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="active")

    site: Mapped[Optional["Site"]] = relationship("Site", back_populates="vlans")
