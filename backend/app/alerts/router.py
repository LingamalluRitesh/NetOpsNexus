"""
FastAPI REST API router for Alert Rules, Active Alerts, and Suppression.
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission, get_current_user
from backend.app.auth.models import User
from backend.app.rbac.permissions import Permission
from backend.app.alerts.models import AlertSeverity, AlertStatus, AlertRule
from backend.app.alerts.schemas import (
    AlertRuleCreate, AlertRuleResponse, AlertResponse, AlertAcknowledgeRequest, AlertSilenceRequest
)
from backend.app.alerts.service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerting Engine"])


@router.get("/rules", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.ALERTS_READ)),
) -> Any:
    """List all configured threshold alert rules."""
    return await AlertService.list_rules(db)


@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    data: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.ALERTS_WRITE)),
) -> Any:
    """Create a new threshold alert rule."""
    return await AlertService.create_rule(db, data)


@router.get("", response_model=List[AlertResponse])
async def list_active_alerts(
    status: Optional[AlertStatus] = None,
    severity: Optional[AlertSeverity] = None,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.ALERTS_READ)),
) -> Any:
    """List live alarms and alerts."""
    return await AlertService.list_alerts(db, status=status, severity=severity, limit=limit)


@router.post("/acknowledge")
async def acknowledge_alerts(
    req: AlertAcknowledgeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.ALERTS_ACK)),
) -> Any:
    """Acknowledge one or multiple active alerts."""
    acked_ids = await AlertService.acknowledge_alerts(db, req, user_id=current_user.id)
    return {"message": f"Successfully acknowledged {len(acked_ids)} alerts", "alert_ids": acked_ids}


@router.post("/silence")
async def silence_device_alerts(
    req: AlertSilenceRequest,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.ALERTS_WRITE)),
) -> Any:
    """Silence alarms for device during scheduled maintenance window."""
    supp = await AlertService.silence_device(db, req)
    return {"message": f"Alerts suppressed for device {req.device_id} until {supp.ends_at.isoformat()}"}
