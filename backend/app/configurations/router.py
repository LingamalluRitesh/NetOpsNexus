"""
FastAPI REST API router for Configuration Management (NCM), Diffs, Templates, Deployments, and Rollbacks.
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission, get_current_user
from backend.app.auth.models import User
from backend.app.rbac.permissions import Permission
from backend.app.configurations.schemas import (
    ConfigVersionResponse, ConfigDiffRequest, ConfigDiffResponse,
    ConfigTemplateCreate, ConfigTemplateResponse, ConfigDeploymentCreate,
    ConfigDeploymentResponse, RollbackRequest, TemplateRenderRequest, TemplateRenderResponse
)
from backend.app.configurations.service import ConfigService
from backend.app.configurations.diff_engine import ConfigDiffEngine
from backend.app.configurations.template_engine import ConfigTemplateEngine

router = APIRouter(prefix="/configs", tags=["Configuration Management (NCM)"])


@router.get("/devices/{device_id}/versions", response_model=List[ConfigVersionResponse])
async def get_device_versions(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.CONFIGS_READ)),
) -> Any:
    """List all versioned configuration backups for a device."""
    return await ConfigService.get_device_backup_history(db, device_id)


@router.post("/devices/{device_id}/backup", response_model=ConfigVersionResponse, status_code=status.HTTP_201_CREATED)
async def take_device_backup(
    device_id: int,
    comment: Optional[str] = "Manual snapshot",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.CONFIGS_WRITE)),
) -> Any:
    """Take an instantaneous running-configuration backup snapshot."""
    return await ConfigService.create_device_backup(db, device_id=device_id, comment=comment, user_id=current_user.id)


@router.post("/diff", response_model=ConfigDiffResponse)
async def compare_configurations(
    req: ConfigDiffRequest,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.CONFIGS_READ)),
) -> Any:
    """Compute line-by-line diff between two configuration versions or raw text strings."""
    src_text = req.source_text or ""
    tgt_text = req.target_text or ""
    return ConfigDiffEngine.compare_configs(src_text, tgt_text)


@router.get("/templates", response_model=List[ConfigTemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.CONFIGS_READ)),
) -> Any:
    """List all Jinja2 configuration templates."""
    return await ConfigService.list_templates(db)


@router.post("/templates", response_model=ConfigTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    data: ConfigTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.CONFIGS_WRITE)),
) -> Any:
    """Create a new parameterized configuration template."""
    return await ConfigService.create_template(db, data, user_id=current_user.id)


@router.post("/templates/render", response_model=TemplateRenderResponse)
async def render_template(
    req: TemplateRenderRequest,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.CONFIGS_READ)),
) -> Any:
    """Dry-run render Jinja2 configuration template with supplied variables."""
    templates = await ConfigService.list_templates(db)
    tmpl = next((t for t in templates if t.id == req.template_id), None)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")

    t_engine = ConfigTemplateEngine()
    return t_engine.render_template(tmpl.template_text, req.variables)


@router.post("/deploy", response_model=ConfigDeploymentResponse, status_code=status.HTTP_201_CREATED)
async def create_and_deploy(
    data: ConfigDeploymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.CONFIGS_DEPLOY)),
) -> Any:
    """Stage a configuration deployment across one or multiple devices."""
    return await ConfigService.create_deployment(db, data, user_id=current_user.id)


@router.post("/deployments/{deployment_id}/approve", response_model=ConfigDeploymentResponse)
async def approve_deployment(
    deployment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.CONFIGS_DEPLOY)),
) -> Any:
    """Approve and trigger execution of staged configuration deployment."""
    return await ConfigService.approve_and_deploy(db, deployment_id, user_id=current_user.id)


@router.post("/rollback", response_model=ConfigVersionResponse)
async def rollback_configuration(
    req: RollbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.CONFIGS_ROLLBACK)),
) -> Any:
    """Atomic rollback: Revert device configuration to a previous snapshot."""
    return await ConfigService.rollback_device(db, req, user_id=current_user.id)
