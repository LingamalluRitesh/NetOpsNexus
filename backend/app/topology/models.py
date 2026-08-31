"""
SQLAlchemy ORM models for Network Links and Topology Layout Coordinates.
"""

from typing import Optional
from sqlalchemy import String, Integer, Float, BigInteger, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import enum
from backend.app.database import Base


class LinkType(str, enum.Enum):
    PHYSICAL = "physical"
    PORT_CHANNEL = "port_channel"
    VLAN_TRUNK = "vlan_trunk"
    VPN_TUNNEL = "vpn_tunnel"
    BGP_PEERING = "bgp_peering"


class LinkStatus(str, enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class NetworkLink(Base):
    __tablename__ = "network_links"

    source_device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    source_interface_id: Mapped[Optional[int]] = mapped_column(ForeignKey("network_interfaces.id", ondelete="SET NULL"), nullable=True)
    target_device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    target_interface_id: Mapped[Optional[int]] = mapped_column(ForeignKey("network_interfaces.id", ondelete="SET NULL"), nullable=True)

    link_type: Mapped[LinkType] = mapped_column(SQLEnum(LinkType), default=LinkType.PHYSICAL)
    bandwidth_mbps: Mapped[int] = mapped_column(BigInteger, default=1000)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.5)
    packet_loss_pct: Mapped[float] = mapped_column(Float, default=0.0)
    utilization_pct: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[LinkStatus] = mapped_column(SQLEnum(LinkStatus), default=LinkStatus.HEALTHY, index=True)

    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    source_device: Mapped["backend.app.devices.models.Device"] = relationship(
        "backend.app.devices.models.Device", foreign_keys=[source_device_id], lazy="selectin"
    )
    target_device: Mapped["backend.app.devices.models.Device"] = relationship(
        "backend.app.devices.models.Device", foreign_keys=[target_device_id], lazy="selectin"
    )
    source_interface: Mapped[Optional["backend.app.devices.models.NetworkInterface"]] = relationship(
        "backend.app.devices.models.NetworkInterface", foreign_keys=[source_interface_id], lazy="selectin"
    )
    target_interface: Mapped[Optional["backend.app.devices.models.NetworkInterface"]] = relationship(
        "backend.app.devices.models.NetworkInterface", foreign_keys=[target_interface_id], lazy="selectin"
    )


class TopologyLayout(Base):
    __tablename__ = "topology_layouts"

    name: Mapped[str] = mapped_column(String(64), nullable=False)
    site_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sites.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    node_positions: Mapped[dict] = mapped_column(JSON, default=dict)
    is_default: Mapped[bool] = mapped_column(default=False)
