"""
SQLAlchemy ORM models for Time-Series Device, Interface, and BGP Monitoring Metrics.
"""

from typing import Optional
from sqlalchemy import String, Integer, Float, BigInteger, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from backend.app.database import Base


class DeviceMetric(Base):
    __tablename__ = "device_metrics"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    cpu_utilization: Mapped[float] = mapped_column(Float, default=0.0)
    memory_utilization: Mapped[float] = mapped_column(Float, default=0.0)
    temperature_celsius: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    uptime_seconds: Mapped[int] = mapped_column(BigInteger, default=0)
    is_reachable: Mapped[bool] = mapped_column(Boolean, default=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    packet_loss_pct: Mapped[float] = mapped_column(Float, default=0.0)

    device: Mapped["backend.app.devices.models.Device"] = relationship("backend.app.devices.models.Device", lazy="selectin")


class InterfaceMetric(Base):
    __tablename__ = "interface_metrics"

    interface_id: Mapped[int] = mapped_column(ForeignKey("network_interfaces.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    rx_bps: Mapped[float] = mapped_column(Float, default=0.0)
    tx_bps: Mapped[float] = mapped_column(Float, default=0.0)
    rx_pps: Mapped[float] = mapped_column(Float, default=0.0)
    tx_pps: Mapped[float] = mapped_column(Float, default=0.0)
    rx_errors: Mapped[int] = mapped_column(BigInteger, default=0)
    tx_errors: Mapped[int] = mapped_column(BigInteger, default=0)
    rx_drops: Mapped[int] = mapped_column(BigInteger, default=0)
    tx_drops: Mapped[int] = mapped_column(BigInteger, default=0)
    utilization_pct: Mapped[float] = mapped_column(Float, default=0.0)

    interface: Mapped["backend.app.devices.models.NetworkInterface"] = relationship("backend.app.devices.models.NetworkInterface", lazy="selectin")


class BgpPeerMetric(Base):
    __tablename__ = "bgp_peer_metrics"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    peer_ip: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    peer_as: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(32), default="Established")
    prefixes_received: Mapped[int] = mapped_column(Integer, default=0)
    uptime_seconds: Mapped[int] = mapped_column(BigInteger, default=0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
