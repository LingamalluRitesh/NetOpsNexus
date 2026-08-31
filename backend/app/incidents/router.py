"""
FastAPI REST API router for Incident Management, Events, and RCA generation.
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission, get_current_user
from backend.app.auth.models import User
from backend.app.rbac.permissions import Permission
from backend.app.incidents.models import IncidentSeverity, IncidentPriority, IncidentStatus
from backend.app.incidents.schemas import (
    IncidentCreate, IncidentUpdate, IncidentResponse, IncidentEventCreate,
    IncidentEventResponse, RcaGenerateRequest, MttrAnalyticsResponse
)
from backend.app.incidents.service import IncidentService

router = APIRouter(prefix="/incidents", tags=["Incident Management"])


@router.get("", response_model=List[IncidentResponse])
async def list_incidents(
    status: Optional[IncidentStatus] = None,
    severity: Optional[IncidentSeverity] = None,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.INCIDENTS_READ)),
) -> Any:
    """List operational incidents with status and severity filters."""
    return await IncidentService.list_incidents(db, status_filter=status, severity=severity, limit=limit)


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    data: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INCIDENTS_CREATE)),
) -> Any:
    """Open a new network incident ticket."""
    return await IncidentService.create_incident(db, data, user_id=current_user.id)


@router.get("/analytics/mttr", response_model=MttrAnalyticsResponse)
async def get_mttr_analytics(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.INCIDENTS_READ)),
) -> Any:
    """Retrieve Mean Time to Resolution (MTTR) and MTTD analytics."""
    return await IncidentService.get_mttr_analytics(db)


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.INCIDENTS_READ)),
) -> Any:
    """Retrieve detailed incident ticket with timeline events."""
    return await IncidentService.get_incident(db, incident_id)


@router.put("/{incident_id}/assign", response_model=IncidentResponse)
async def assign_incident(
    incident_id: int,
    assignee_id: int = Query(..., description="Target User ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INCIDENTS_ASSIGN)),
) -> Any:
    """Assign incident to an engineer and transition to INVESTIGATING status."""
    return await IncidentService.assign_incident(db, incident_id, assign_to_id=assignee_id, user_id=current_user.id)


@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: int,
    notes: str = Query(..., min_length=5),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INCIDENTS_WRITE)),
) -> Any:
    """Resolve incident and compute MTTR duration."""
    return await IncidentService.resolve_incident(db, incident_id, notes=notes, user_id=current_user.id)


@router.post("/{incident_id}/events", response_model=IncidentEventResponse)
async def add_incident_event(
    incident_id: int,
    data: IncidentEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.INCIDENTS_WRITE)),
) -> Any:
    """Add comment or investigation event to incident timeline."""
    return await IncidentService.add_event(db, incident_id, data, user_id=current_user.id)


@router.post("/{incident_id}/rca")
async def generate_rca_report(
    incident_id: int,
    req: RcaGenerateRequest,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.INCIDENTS_WRITE)),
) -> Any:
    """Generate structured Root Cause Analysis post-mortem report."""
    return await IncidentService.generate_rca(db, incident_id, req)
