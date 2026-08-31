"""
FastAPI REST API router for network telemetry and monitoring dashboards.
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission
from backend.app.rbac.permissions import Permission
from backend.app.monitoring.schemas import (
    MonitoringOverviewResponse, DeviceTelemetryHistory, DeviceMetricResponse
)
from backend.app.monitoring.service import MonitoringService
from backend.app.monitoring.collector import TelemetryCollector

router = APIRouter(prefix="/monitoring", tags=["Network Monitoring & Telemetry"])


@router.get("/overview", response_model=MonitoringOverviewResponse)
async def get_monitoring_overview(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.MONITORING_READ)),
) -> Any:
    """Retrieve operational NOC monitoring overview metrics."""
    return await MonitoringService.get_overview(db)


@router.get("/devices/{device_id}", response_model=DeviceTelemetryHistory)
async def get_device_telemetry(
    device_id: int,
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.MONITORING_READ)),
) -> Any:
    """Fetch time-series CPU, RAM, latency, and loss graphs for device."""
    return await MonitoringService.get_device_history(db, device_id, hours=hours)


@router.post("/poll-now")
async def trigger_poll_cycle(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.MONITORING_WRITE)),
) -> Any:
    """Manually trigger a telemetry collection poll cycle across all devices."""
    await TelemetryCollector.run_poll_cycle()
    return {"message": "Telemetry poll cycle completed successfully"}
