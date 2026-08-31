"""
SQLAlchemy ORM models for VRF, IPv4/IPv6 Subnets, IP Addresses, and IP Conflicts.
"""

from typing import List, Optional
from sqlalchemy import String, Integer, Float, BigInteger, DateTime, ForeignKey, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import enum
from backend.app.database import Base
import backend.app.devices.models


class SubnetStatus(str, enum.Enum):
    ACTIVE = "active"
    RESERVED = "reserved"
    DEPRECATED = "deprecated"


class IpStatus(str, enum.Enum):
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    FREE = "free"
    CONFLICT = "conflict"


class Vrf(Base):
    __tablename__ = "vrfs"

    name: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    rd: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True)  # Route Distinguisher e.g. 65000:100
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    subnets: Mapped[List["Subnet"]] = relationship("Subnet", back_populates="vrf", lazy="selectin")


class Subnet(Base):
    __tablename__ = "subnets"

    network_address: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    prefix_len: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ip_version: Mapped[int] = mapped_column(Integer, default=4)  # 4 or 6
    
    vrf_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vrfs.id", ondelete="SET NULL"), nullable=True, index=True)
    site_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sites.id", ondelete="SET NULL"), nullable=True, index=True)
    vlan_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gateway_ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    total_ips: Mapped[int] = mapped_column(BigInteger, default=256)
    used_ips: Mapped[int] = mapped_column(BigInteger, default=0)
    reserved_ips: Mapped[int] = mapped_column(BigInteger, default=0)
    status: Mapped[SubnetStatus] = mapped_column(SQLEnum(SubnetStatus), default=SubnetStatus.ACTIVE, index=True)

    # Relationships
    vrf: Mapped[Optional["Vrf"]] = relationship("Vrf", back_populates="subnets")
    site: Mapped[Optional["backend.app.devices.models.Site"]] = relationship("backend.app.devices.models.Site", lazy="selectin")
    ip_addresses: Mapped[List["IpAddress"]] = relationship("IpAddress", back_populates="subnet", cascade="all, delete-orphan", lazy="selectin")


class IpAddress(Base):
    __tablename__ = "ip_addresses"

    subnet_id: Mapped[int] = mapped_column(ForeignKey("subnets.id", ondelete="CASCADE"), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[IpStatus] = mapped_column(SQLEnum(IpStatus), default=IpStatus.ALLOCATED, index=True)
    
    fqdn: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    interface_id: Mapped[Optional[int]] = mapped_column(ForeignKey("network_interfaces.id", ondelete="SET NULL"), nullable=True)
    
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_dhcp: Mapped[bool] = mapped_column(Boolean, default=False)
    allocated_to: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    subnet: Mapped["Subnet"] = relationship("Subnet", back_populates="ip_addresses")


class IpConflict(Base):
    __tablename__ = "ip_conflicts"

    ip_address: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subnet_id: Mapped[int] = mapped_column(ForeignKey("subnets.id", ondelete="CASCADE"), nullable=False, index=True)
    conflicting_macs: Mapped[List[str]] = mapped_column(JSON, default=list)
    conflicting_device_ids: Mapped[List[int]] = mapped_column(JSON, default=list)
    
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
