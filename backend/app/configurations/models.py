"""
SQLAlchemy ORM models for Network Configuration Backups, Jinja2 Templates, Deployments, and Rollback logs.
"""

from typing import List, Optional
from sqlalchemy import String, Integer, BigInteger, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import enum
from backend.app.database import Base


class BackupType(str, enum.Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    PRE_DEPLOYMENT = "pre_deployment"
    POST_DEPLOYMENT = "post_deployment"
    ROLLBACK_RESTORE = "rollback_restore"


class DeploymentStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    DEPLOYING = "deploying"
    VERIFIED = "verified"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeviceConfig(Base):
    __tablename__ = "device_configs"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    config_text: Mapped[str] = mapped_column(Text, nullable=False)
    config_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256
    backup_type: Mapped[BackupType] = mapped_column(SQLEnum(BackupType), default=BackupType.MANUAL)
    created_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    device: Mapped["backend.app.devices.models.Device"] = relationship("backend.app.devices.models.Device", lazy="selectin")
    created_by: Mapped[Optional["backend.app.auth.models.User"]] = relationship("backend.app.auth.models.User", lazy="selectin")


class ConfigTemplate(Base):
    __tablename__ = "config_templates"

    name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    vendor: Mapped[str] = mapped_column(String(64), nullable=False)
    os_type: Mapped[str] = mapped_column(String(64), nullable=False)
    template_text: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    schema_variables: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)  # Variable names and defaults
    created_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ConfigDeployment(Base):
    __tablename__ = "config_deployments"

    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[DeploymentStatus] = mapped_column(SQLEnum(DeploymentStatus), default=DeploymentStatus.DRAFT, index=True)
    
    target_device_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False)
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("config_templates.id", ondelete="SET NULL"), nullable=True)
    template_vars: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    raw_config_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    pre_checks: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    post_checks: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    approval_required: Mapped[bool] = mapped_column(Boolean, default=True)
    approved_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    template: Mapped[Optional["ConfigTemplate"]] = relationship("ConfigTemplate", lazy="selectin")
    logs: Mapped[List["DeploymentLog"]] = relationship("DeploymentLog", back_populates="deployment", cascade="all, delete-orphan", lazy="selectin")


class DeploymentLog(Base):
    __tablename__ = "deployment_logs"

    deployment_id: Mapped[int] = mapped_column(ForeignKey("config_deployments.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    step_name: Mapped[str] = mapped_column(String(64), nullable=False)  # pre_check, backup, apply, verify, rollback
    status: Mapped[str] = mapped_column(String(32), default="success")  # success, warning, failed
    log_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    diff_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rollback_version_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    deployment: Mapped["ConfigDeployment"] = relationship("ConfigDeployment", back_populates="logs")
    device: Mapped["backend.app.devices.models.Device"] = relationship("backend.app.devices.models.Device", lazy="selectin")
