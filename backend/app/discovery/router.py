"""
FastAPI REST API router for network discovery operations.
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission
from backend.app.rbac.permissions import Permission
from backend.app.discovery.schemas import DiscoveryScanConfig, DiscoveryJobResponse, ImportDiscoveredRequest
from backend.app.discovery.service import DiscoveryService
from backend.app.devices.schemas import DeviceResponse

router = APIRouter(prefix="/discovery", tags=["Network Discovery"])


@router.post("/scan", response_model=DiscoveryJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_discovery_scan(
    config: DiscoveryScanConfig,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DISCOVERY_RUN)),
) -> Any:
    """Launch an asynchronous multi-protocol network discovery scan."""
    return await DiscoveryService.create_and_start_job(db, config)


@router.get("/jobs", response_model=List[DiscoveryJobResponse])
async def list_discovery_jobs(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DISCOVERY_READ)),
) -> Any:
    """List recent discovery scan jobs and execution progress."""
    return await DiscoveryService.list_jobs(db, limit=limit)


@router.get("/jobs/{job_id}", response_model=DiscoveryJobResponse)
async def get_discovery_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DISCOVERY_READ)),
) -> Any:
    """Retrieve detailed discovery job status and discovered device list."""
    return await DiscoveryService.get_job(db, job_id)


@router.post("/import", response_model=List[DeviceResponse])
async def import_discovered_devices(
    req: ImportDiscoveredRequest,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DEVICES_WRITE)),
) -> Any:
    """Import selected discovered devices into core managed device inventory."""
    return await DiscoveryService.import_devices(db, req)
