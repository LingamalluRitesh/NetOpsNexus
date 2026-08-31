"""
Service layer for Workflow management, library templates, and asynchronous run execution.
"""

from typing import List, Optional, Tuple, Dict, Any
import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.automation.models import Workflow, WorkflowRun, WorkflowStepLog, TriggerType, WorkflowRunStatus
from backend.app.automation.schemas import (
    WorkflowCreate, WorkflowResponse, WorkflowRunResponse, WorkflowRunTriggerRequest
)
from backend.app.automation.dag_engine import DagEngine


class AutomationService:
    @staticmethod
    async def list_workflows(db: AsyncSession) -> List[Workflow]:
        stmt = select(Workflow).order_by(Workflow.name)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_workflow(db: AsyncSession, workflow_id: int) -> Workflow:
        stmt = select(Workflow).options(selectinload(Workflow.runs)).where(Workflow.id == workflow_id)
        res = await db.execute(stmt)
        wf = res.scalar_one_or_none()
        if not wf:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
        return wf

    @staticmethod
    async def create_workflow(db: AsyncSession, data: WorkflowCreate, user_id: Optional[int] = None) -> Workflow:
        wf = Workflow(
            name=data.name,
            description=data.description,
            trigger_type=data.trigger_type,
            cron_expression=data.cron_expression,
            is_active=data.is_active,
            definition=data.definition.model_dump(),
            created_by_id=user_id,
        )
        db.add(wf)
        await db.commit()
        await db.refresh(wf)
        return wf

    @staticmethod
    async def trigger_workflow(db: AsyncSession, workflow_id: int, trigger_source: str = "manual", payload: Optional[Dict[str, Any]] = None) -> WorkflowRun:
        """Instantiate a new WorkflowRun and launch DAG execution asynchronously."""
        wf = await AutomationService.get_workflow(db, workflow_id)
        
        run = WorkflowRun(
            workflow_id=wf.id,
            trigger_source=trigger_source,
            status=WorkflowRunStatus.RUNNING,
            trigger_payload=payload or {},
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)

        # Run DAG pipeline
        return await DagEngine.execute_workflow(db, run, wf.definition)

    @staticmethod
    async def list_runs(db: AsyncSession, workflow_id: Optional[int] = None, limit: int = 50) -> List[WorkflowRun]:
        stmt = select(WorkflowRun).options(selectinload(WorkflowRun.step_logs)).order_by(desc(WorkflowRun.started_at)).limit(limit)
        if workflow_id:
            stmt = stmt.where(WorkflowRun.workflow_id == workflow_id)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_run(db: AsyncSession, run_id: int) -> WorkflowRun:
        stmt = select(WorkflowRun).options(selectinload(WorkflowRun.step_logs)).where(WorkflowRun.id == run_id)
        res = await db.execute(stmt)
        run = res.scalar_one_or_none()
        if not run:
            raise HTTPException(status_code=404, detail=f"Workflow run {run_id} not found")
        return run
