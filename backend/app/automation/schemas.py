"""
Pydantic schemas for Workflow Automation DAG nodes, definitions, and run executions.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from backend.app.automation.models import TriggerType, WorkflowRunStatus


class WorkflowNode(BaseModel):
    id: str
    type: str  # trigger, condition, action, verification, rollback
    label: str
    action_name: Optional[str] = None
    parameters: Dict[str, Any] = {}
    x: Optional[float] = 0.0
    y: Optional[float] = 0.0


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    condition: Optional[str] = None  # on_success, on_failure, always


class WorkflowDefinition(BaseModel):
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]


class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    description: Optional[str] = None
    trigger_type: TriggerType = TriggerType.MANUAL
    cron_expression: Optional[str] = None
    is_active: bool = True
    definition: WorkflowDefinition


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowResponse(WorkflowBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class WorkflowStepLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    node_id: str
    node_type: str
    action_name: Optional[str] = None
    status: str
    input_params: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    execution_time_ms: float
    started_at: datetime
    completed_at: Optional[datetime] = None


class WorkflowRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workflow_id: int
    trigger_source: str
    status: WorkflowRunStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    step_logs: List[WorkflowStepLogResponse] = []


class WorkflowRunTriggerRequest(BaseModel):
    trigger_payload: Optional[Dict[str, Any]] = None


class ActionParamSchema(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


class ActionDefinitionResponse(BaseModel):
    action_name: str
    category: str
    label: str
    description: str
    parameters: List[ActionParamSchema]
