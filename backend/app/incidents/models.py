"""
SQLAlchemy ORM models for Incidents, Incident Events, Runbooks, and RCA Reports.
"""

from typing import List, Optional
from sqlalchemy import String, Integer, BigInteger, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import enum
from backend.app.database import Base


class IncidentSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentPriority(str, enum.Enum):
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"
    P4 = "p4"


class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Incident(Base):
    __tablename__ = "incidents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[IncidentSeverity] = mapped_column(SQLEnum(IncidentSeverity), default=IncidentSeverity.MEDIUM, index=True)
    priority: Mapped[IncidentPriority] = mapped_column(SQLEnum(IncidentPriority), default=IncidentPriority.P3, index=True)
    status: Mapped[IncidentStatus] = mapped_column(SQLEnum(IncidentStatus), default=IncidentStatus.OPEN, index=True)
    
    assigned_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    affected_device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    related_alert_ids: Mapped[Optional[List[int]]] = mapped_column(JSON, default=list)
    
    runbook_id: Mapped[Optional[int]] = mapped_column(ForeignKey("runbooks.id", ondelete="SET NULL"), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    root_cause_analysis: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    mttr_seconds: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Relationships
    assigned_to: Mapped[Optional["backend.app.auth.models.User"]] = relationship("backend.app.auth.models.User", lazy="selectin")
    affected_device: Mapped[Optional["backend.app.devices.models.Device"]] = relationship("backend.app.devices.models.Device", lazy="selectin")
    runbook: Mapped[Optional["Runbook"]] = relationship("Runbook", lazy="selectin")
    events: Mapped[List["IncidentEvent"]] = relationship("IncidentEvent", back_populates="incident", cascade="all, delete-orphan", lazy="selectin")


class Runbook(Base):
    __tablename__ = "runbooks"

    title: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    steps: Mapped[List[dict]] = mapped_column(JSON, default=list)  # [{"step": 1, "title": "Check BGP", "action": "show bgp"}]
    is_automated: Mapped[bool] = mapped_column(Boolean, default=False)


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    incident_id: Mapped[int] = mapped_column(ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), default="comment")  # comment, status_change, assignment, remediation_step
    message: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    incident: Mapped["Incident"] = relationship("Incident", back_populates="events")
    author: Mapped[Optional["backend.app.auth.models.User"]] = relationship("backend.app.auth.models.User", lazy="selectin")
