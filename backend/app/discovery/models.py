"""
SQLAlchemy ORM models for Network Discovery Jobs and Discovered Devices.
"""

from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import enum
from backend.app.database import Base


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanType(str, enum.Enum):
    QUICK_PING = "quick_ping"
    STANDARD_PORTS = "standard_ports"
    FULL_DISCOVERY = "full_discovery"
    DEEP_PROBE = "deep_probe"


class DiscoveryJob(Base):
    __tablename__ = "discovery_jobs"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    target_cidr: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    scan_type: Mapped[ScanType] = mapped_column(SQLEnum(ScanType), default=ScanType.FULL_DISCOVERY)
    status: Mapped[JobStatus] = mapped_column(SQLEnum(JobStatus), default=JobStatus.QUEUED, index=True)
    
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    discovered_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    total_targets: Mapped[int] = mapped_column(Integer, default=0)
    
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    snmp_community: Mapped[Optional[str]] = mapped_column(String(64), default="public")
    credentials_ref: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    discovered_devices: Mapped[List["DiscoveredDevice"]] = relationship(
        "DiscoveredDevice", back_populates="job", cascade="all, delete-orphan", lazy="selectin"
    )


class DiscoveredDevice(Base):
    __tablename__ = "discovered_devices"

    job_id: Mapped[int] = mapped_column(ForeignKey("discovery_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    hostname: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    vendor: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    os_detected: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    open_ports: Mapped[Optional[List[int]]] = mapped_column(JSON, default=list)
    snmp_responsive: Mapped[bool] = mapped_column(Boolean, default=False)
    ssh_responsive: Mapped[bool] = mapped_column(Boolean, default=False)
    lldp_neighbors: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    is_imported: Mapped[bool] = mapped_column(Boolean, default=False)
    response_time_ms: Mapped[Optional[float]] = mapped_column(nullable=True)

    job: Mapped["DiscoveryJob"] = relationship("DiscoveryJob", back_populates="discovered_devices")
