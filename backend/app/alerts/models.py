"""
SQLAlchemy ORM models for Alert Rules, Live Alerts, and Alert Suppression Windows.
"""

from typing import List, Optional
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import enum
from backend.app.database import Base


class AlertSeverity(str, enum.Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    SILENCED = "silenced"
    RESOLVED = "resolved"


class AlertRule(Base):
    __tablename__ = "alert_rules"

    name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    metric_name: Mapped[str] = mapped_column(String(64), nullable=False)  # cpu, memory, latency, packet_loss, interface_down
    condition_op: Mapped[str] = mapped_column(String(8), default="gt")  # gt, lt, eq, ne
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=300)
    severity: Mapped[AlertSeverity] = mapped_column(SQLEnum(AlertSeverity), default=AlertSeverity.WARNING)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_create_incident: Mapped[bool] = mapped_column(Boolean, default=False)
    incident_priority: Mapped[str] = mapped_column(String(8), default="p2")

    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="rule", lazy="selectin")


class Alert(Base):
    __tablename__ = "alerts"

    rule_id: Mapped[Optional[int]] = mapped_column(ForeignKey("alert_rules.id", ondelete="SET NULL"), nullable=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(64), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[AlertSeverity] = mapped_column(SQLEnum(AlertSeverity), default=AlertSeverity.WARNING, index=True)
    status: Mapped[AlertStatus] = mapped_column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE, index=True)
    
    acknowledged_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    rule: Mapped[Optional["AlertRule"]] = relationship("AlertRule", back_populates="alerts")
    device: Mapped["backend.app.devices.models.Device"] = relationship("backend.app.devices.models.Device", lazy="selectin")
    acknowledged_by: Mapped[Optional["backend.app.auth.models.User"]] = relationship("backend.app.auth.models.User", lazy="selectin")


class AlertSuppression(Base):
    __tablename__ = "alert_suppressions"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)  # Maintenance window
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
