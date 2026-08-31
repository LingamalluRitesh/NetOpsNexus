"""
FastAPI REST API router for Topology Graph, Path Tracing, and Blast Radius Analysis.
"""

from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission, get_current_user
from backend.app.auth.models import User
from backend.app.rbac.permissions import Permission
from backend.app.topology.schemas import (
    TopologyGraphResponse, PathTraceRequest, PathTraceResponse,
    DependencyAnalysisResponse, SpofReportResponse, LayoutSaveRequest
)
from backend.app.topology.service import TopologyService

router = APIRouter(prefix="/topology", tags=["Network Topology Engine"])


@router.get("", response_model=TopologyGraphResponse)
async def get_topology(
    site_id: Optional[int] = Query(None, description="Optional site filter"),
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.TOPOLOGY_READ)),
) -> Any:
    """Fetch complete live topology graph (nodes, edges, metrics, and health states)."""
    return await TopologyService.get_topology_graph(db, site_id=site_id)


@router.post("/path-trace", response_model=PathTraceResponse)
async def trace_path(
    req: PathTraceRequest,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.TOPOLOGY_READ)),
) -> Any:
    """Compute optimal shortest path and redundant backup routes between two devices."""
    return await TopologyService.trace_path(db, req)


@router.get("/dependencies/{device_id}", response_model=DependencyAnalysisResponse)
async def get_device_dependencies(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.TOPOLOGY_READ)),
) -> Any:
    """Calculate upstream dependencies, downstream impact, and failure blast radius for a device."""
    return await TopologyService.analyze_dependencies(db, device_id)


@router.get("/spof", response_model=SpofReportResponse)
async def get_spof_report(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.TOPOLOGY_READ)),
) -> Any:
    """Identify all Single Points of Failure and critical bridge links across the network topology."""
    return await TopologyService.get_spof_report(db)


@router.post("/layout")
async def save_layout(
    req: LayoutSaveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.TOPOLOGY_WRITE)),
) -> Any:
    """Persist custom node coordinates on interactive topology canvas."""
    return await TopologyService.save_layout(db, req, user_id=current_user.id)
