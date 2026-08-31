"""
FastAPI REST API router for Network Automation Workflows and Action Catalog.
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission, get_current_user
from backend.app.auth.models import User
from backend.app.rbac.permissions import Permission
from backend.app.automation.schemas import (
    WorkflowCreate, WorkflowResponse, WorkflowRunResponse, WorkflowRunTriggerRequest,
    ActionDefinitionResponse
)
from backend.app.automation.service import AutomationService
from backend.app.automation.action_catalog import ActionCatalog

router = APIRouter(prefix="/automation", tags=["Workflow Automation Engine"])


@router.get("/actions", response_model=List[ActionDefinitionResponse])
async def list_action_catalog(
    _: Any = Depends(require_permission(Permission.AUTOMATION_READ)),
) -> Any:
    """List all available built-in network operational actions."""
    return ActionCatalog.list_actions()


@router.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.AUTOMATION_READ)),
) -> Any:
    """List all configured automation workflows."""
    return await AutomationService.list_workflows(db)


@router.post("/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.AUTOMATION_WRITE)),
) -> Any:
    """Create a new visual DAG automation workflow."""
    return await AutomationService.create_workflow(db, data, user_id=current_user.id)


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.AUTOMATION_READ)),
) -> Any:
    """Retrieve detailed workflow graph definition."""
    return await AutomationService.get_workflow(db, workflow_id)


@router.post("/workflows/{workflow_id}/run", response_model=WorkflowRunResponse)
async def trigger_workflow(
    workflow_id: int,
    req: WorkflowRunTriggerRequest,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.AUTOMATION_EXECUTE)),
) -> Any:
    """Trigger manual execution of an automation workflow."""
    return await AutomationService.trigger_workflow(db, workflow_id, trigger_source="manual", payload=req.trigger_payload)


@router.get("/runs", response_model=List[WorkflowRunResponse])
async def list_runs(
    workflow_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.AUTOMATION_READ)),
) -> Any:
    """List recent workflow execution runs and logs."""
    return await AutomationService.list_runs(db, workflow_id=workflow_id, limit=limit)


@router.get("/runs/{run_id}", response_model=WorkflowRunResponse)
async def get_run(
    run_id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.AUTOMATION_READ)),
) -> Any:
    """Retrieve detailed execution trace and step-by-step logs of a run."""
    return await AutomationService.get_run(db, run_id)
