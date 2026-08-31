"""
Pydantic schemas for Network Configuration Management (NCM), Templates, Diffing, and Deployment.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from backend.app.configurations.models import BackupType, DeploymentStatus


class ConfigVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    version_number: int
    config_text: str
    config_hash: str
    backup_type: BackupType
    created_by_id: Optional[int] = None
    comment: Optional[str] = None
    created_at: datetime


class ConfigDiffRequest(BaseModel):
    device_id: Optional[int] = None
    source_config_id: Optional[int] = None
    target_config_id: Optional[int] = None
    source_text: Optional[str] = None
    target_text: Optional[str] = None


class DiffLine(BaseModel):
    line_number_src: Optional[int] = None
    line_number_dst: Optional[int] = None
    type: str  # unchanged, added, removed, modified
    content: str


class ConfigDiffResponse(BaseModel):
    unified_diff: str
    diff_lines: List[DiffLine]
    additions: int
    deletions: int
    modifications: int
    is_identical: bool


class ConfigTemplateBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    vendor: str
    os_type: str = "cisco_ios"
    template_text: str = Field(..., min_length=1)
    description: Optional[str] = None
    schema_variables: Optional[Dict[str, Any]] = None
    is_active: bool = True


class ConfigTemplateCreate(ConfigTemplateBase):
    pass


class ConfigTemplateResponse(ConfigTemplateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_id: Optional[int] = None
    created_at: datetime


class TemplateRenderRequest(BaseModel):
    template_id: int
    variables: Dict[str, Any]


class TemplateRenderResponse(BaseModel):
    rendered_config: str
    variables_used: Dict[str, Any]
    syntax_valid: bool
    errors: List[str] = []


class ConfigDeploymentCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=128)
    description: Optional[str] = None
    target_device_ids: List[int] = Field(..., min_length=1)
    template_id: Optional[int] = None
    template_vars: Optional[Dict[str, Any]] = None
    raw_config_text: Optional[str] = None
    approval_required: bool = True


class DeploymentLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    device_hostname: Optional[str] = None
    step_name: str
    status: str
    log_output: Optional[str] = None
    diff_text: Optional[str] = None
    rollback_version_id: Optional[int] = None
    timestamp: datetime


class ConfigDeploymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    status: DeploymentStatus
    target_device_ids: List[int]
    template_id: Optional[int] = None
    template_vars: Optional[Dict[str, Any]] = None
    approval_required: bool
    approved_by_id: Optional[int] = None
    created_by_id: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    logs: List[DeploymentLogResponse] = []


class RollbackRequest(BaseModel):
    device_id: int
    target_version_id: int
    comment: Optional[str] = "Manual Rollback Restore"
