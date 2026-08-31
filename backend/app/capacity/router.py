"""
FastAPI REST API router for Capacity Planning and Saturation Forecasting.
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission
from backend.app.rbac.permissions import Permission
from backend.app.capacity.schemas import CapacityOverviewResponse
from backend.app.capacity.service import CapacityService

router = APIRouter(prefix="/capacity", tags=["Capacity Planning & Forecasting"])


@router.get("/overview", response_model=CapacityOverviewResponse)
async def get_capacity_overview(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.MONITORING_READ)),
) -> Any:
    """Retrieve bandwidth, CPU, and RAM saturation forecasts and exhaustion timelines."""
    return await CapacityService.get_overview(db)
