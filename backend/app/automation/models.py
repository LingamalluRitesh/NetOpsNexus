"""
SQLAlchemy ORM models for Network Automation Workflows, Runs, and Step Logs.
"""

from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
import enum
from backend.app.database import Base


class TriggerType(str, enum.Enum):
    MANUAL = "manual"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    ALERT = "alert"
    CONFIG_DRIFT = "config_drift"


class WorkflowRunStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class Workflow(Base):
    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    trigger_type: Mapped[TriggerType] = mapped_column(SQLEnum(TriggerType), default=TriggerType.MANUAL, index=True)
    cron_expression: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    definition: Mapped[dict] = mapped_column(JSON, default=dict)  # {"nodes": [...], "edges": [...]}
    created_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    runs: Mapped[List["WorkflowRun"]] = relationship("WorkflowRun", back_populates="workflow", cascade="all, delete-orphan", lazy="selectin")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    trigger_source: Mapped[str] = mapped_column(String(64), default="manual")
    status: Mapped[WorkflowRunStatus] = mapped_column(SQLEnum(WorkflowRunStatus), default=WorkflowRunStatus.RUNNING, index=True)
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    trigger_payload: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="runs")
    step_logs: Mapped[List["WorkflowStepLog"]] = relationship("WorkflowStepLog", back_populates="run", cascade="all, delete-orphan", lazy="selectin")


class WorkflowStepLog(Base):
    __tablename__ = "workflow_step_logs"

    run_id: Mapped[int] = mapped_column(ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id: Mapped[str] = mapped_column(String(64), nullable=False)
    node_type: Mapped[str] = mapped_column(String(64), nullable=False)  # trigger, condition, action, verification
    action_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="success")  # success, skipped, failed
    
    input_params: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    execution_time_ms: Mapped[float] = mapped_column(default=0.0)
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    run: Mapped["WorkflowRun"] = relationship("WorkflowRun", back_populates="step_logs")
