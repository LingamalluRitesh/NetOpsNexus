"""
SQLAlchemy ORM models for Security Audits, CIS Benchmark Findings, ACL Rules, and Rogue Device detections.
"""

from typing import List, Optional
from sqlalchemy import String, Integer, Float, BigInteger, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import enum
from backend.app.database import Base


class SecurityAuditReport(Base):
    __tablename__ = "security_audit_reports"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    score_percent: Mapped[float] = mapped_column(Float, default=0.0)
    cis_passed_checks: Mapped[int] = mapped_column(Integer, default=0)
    cis_failed_checks: Mapped[int] = mapped_column(Integer, default=0)
    findings: Mapped[List[dict]] = mapped_column(JSON, default=list)  # [{"check_id": "CIS-1.1", "status": "FAIL", "description": "Telnet enabled"}]
    audited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    device: Mapped["backend.app.devices.models.Device"] = relationship("backend.app.devices.models.Device", lazy="selectin")


class AclRule(Base):
    __tablename__ = "acl_rules"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    acl_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sequence_num: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(16), default="permit")  # permit, deny
    protocol: Mapped[str] = mapped_column(String(16), default="ip")  # ip, tcp, udp, icmp
    
    src_ip_prefix: Mapped[str] = mapped_column(String(64), default="any")  # e.g. 10.0.0.0/8 or any
    dst_ip_prefix: Mapped[str] = mapped_column(String(64), default="any")
    src_port: Mapped[str] = mapped_column(String(32), default="any")
    dst_port: Mapped[str] = mapped_column(String(32), default="any")  # e.g. 443, 22, any
    
    is_shadowed: Mapped[bool] = mapped_column(Boolean, default=False)
    shadowed_by_sequence: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


class RogueDeviceFinding(Base):
    __tablename__ = "rogue_device_findings"

    mac_address: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    switch_device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"), nullable=True)
    switch_port: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="flagged")  # flagged, approved, quarantined
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    switch_device: Mapped[Optional["backend.app.devices.models.Device"]] = relationship("backend.app.devices.models.Device", lazy="selectin")
