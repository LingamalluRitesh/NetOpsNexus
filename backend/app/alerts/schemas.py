"""
Pydantic schemas for Alert Rules, Live Alerts, and Alert Acknowledgement.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from backend.app.alerts.models import AlertSeverity, AlertStatus


class AlertRuleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    metric_name: str
    condition_op: str = "gt"
    threshold_value: float
    duration_seconds: int = 300
    severity: AlertSeverity = AlertSeverity.WARNING
    is_enabled: bool = True
    auto_create_incident: bool = False
    incident_priority: str = "p2"


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleResponse(AlertRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule_id: Optional[int] = None
    device_id: int
    device_hostname: Optional[str] = None
    message: str
    metric_name: str
    metric_value: float
    severity: AlertSeverity
    status: AlertStatus
    acknowledged_by_id: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    triggered_at: datetime
    resolved_at: Optional[datetime] = None


class AlertAcknowledgeRequest(BaseModel):
    alert_ids: List[int]
    comment: Optional[str] = "Acknowledged by operator"


class AlertSilenceRequest(BaseModel):
    device_id: int
    duration_minutes: int = 60
    reason: str = "Maintenance window"
