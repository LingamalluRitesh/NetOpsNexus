"""
SQLAlchemy ORM models for Immutable Security and Operations Audit Trail.
"""

from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from backend.app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # create, update, delete, deploy, rollback, cli_execute
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # device, config, workflow, incident, rbac
    resource_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    user: Mapped[Optional["backend.app.auth.models.User"]] = relationship("backend.app.auth.models.User", lazy="selectin")
