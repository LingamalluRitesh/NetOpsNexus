"""
FastAPI REST API router for the 7-Component Health Score Engine.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission
from backend.app.rbac.permissions import Permission
from backend.app.health.schemas import DeviceHealthReport, FleetHealthOverview
from backend.app.health.service import HealthService

router = APIRouter(prefix="/health", tags=["Health Score Engine"])


@router.get("/fleet", response_model=FleetHealthOverview)
async def get_fleet_health(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.MONITORING_READ)),
) -> Any:
    """Retrieve aggregate enterprise fleet health score and grade."""
    return await HealthService.get_fleet_health(db)


@router.get("/devices/{device_id}", response_model=DeviceHealthReport)
async def get_device_health(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.MONITORING_READ)),
) -> Any:
    """Retrieve 7-component granular health breakdown for device."""
    return await HealthService.get_device_health(db, device_id)
