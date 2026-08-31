"""
Pydantic schemas for Incident Management, Events, Runbooks, and MTTR Analytics.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from backend.app.incidents.models import IncidentSeverity, IncidentPriority, IncidentStatus


class RunbookBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=128)
    description: str
    steps: List[Dict[str, Any]] = []
    is_automated: bool = False


class RunbookCreate(RunbookBase):
    pass


class RunbookResponse(RunbookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class IncidentEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    event_type: str
    message: str
    author_id: Optional[int] = None
    created_at: datetime


class IncidentEventCreate(BaseModel):
    event_type: str = "comment"
    message: str = Field(..., min_length=1)


class IncidentBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    priority: IncidentPriority = IncidentPriority.P3
    status: IncidentStatus = IncidentStatus.OPEN
    assigned_to_id: Optional[int] = None
    affected_device_id: Optional[int] = None
    runbook_id: Optional[int] = None


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    priority: Optional[IncidentPriority] = None
    status: Optional[IncidentStatus] = None
    assigned_to_id: Optional[int] = None
    resolution_notes: Optional[str] = None


class IncidentResponse(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    opened_at: datetime
    resolved_at: Optional[datetime] = None
    mttr_seconds: Optional[int] = None
    resolution_notes: Optional[str] = None
    root_cause_analysis: Optional[Dict[str, Any]] = None
    events: List[IncidentEventResponse] = []


class RcaGenerateRequest(BaseModel):
    root_cause_summary: str
    impacted_services: List[str]
    preventative_actions: List[str]
    remediation_steps_taken: List[str]


class MttrAnalyticsResponse(BaseModel):
    total_incidents_30d: int
    mean_time_to_resolution_minutes: float
    mean_time_to_detect_minutes: float
    p1_incidents_count: int
    p2_incidents_count: int
    p3_incidents_count: int
    p4_incidents_count: int
    resolution_rate_pct: float
