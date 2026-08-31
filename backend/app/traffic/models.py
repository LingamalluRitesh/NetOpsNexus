"""
SQLAlchemy ORM models for NetFlow and sFlow traffic flow records.
"""

from typing import Optional
from sqlalchemy import String, Integer, Float, BigInteger, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from backend.app.database import Base


class TrafficFlowRecord(Base):
    __tablename__ = "traffic_flow_records"

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    interface_id: Mapped[Optional[int]] = mapped_column(ForeignKey("network_interfaces.id", ondelete="SET NULL"), nullable=True)
    
    src_ip: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    dst_ip: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    src_port: Mapped[int] = mapped_column(Integer, default=0)
    dst_port: Mapped[int] = mapped_column(Integer, default=0, index=True)
    protocol: Mapped[str] = mapped_column(String(16), default="TCP")  # TCP, UDP, ICMP
    
    bytes_count: Mapped[int] = mapped_column(BigInteger, default=0)
    packets_count: Mapped[int] = mapped_column(BigInteger, default=0)
    application_name: Mapped[str] = mapped_column(String(64), default="HTTPS", index=True)

    __table_args__ = (
        Index("ix_flow_src_dst", "src_ip", "dst_ip"),
    )
