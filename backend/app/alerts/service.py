"""
Service layer for Alert rules, active alerts stream, acknowledgement, and silencing.
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.alerts.models import AlertRule, Alert, AlertSuppression, AlertStatus, AlertSeverity
from backend.app.alerts.schemas import (
    AlertRuleCreate, AlertAcknowledgeRequest, AlertSilenceRequest, AlertResponse
)


class AlertService:
    @staticmethod
    async def list_rules(db: AsyncSession) -> List[AlertRule]:
        stmt = select(AlertRule).order_by(AlertRule.name)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_rule(db: AsyncSession, data: AlertRuleCreate) -> AlertRule:
        rule = AlertRule(**data.model_dump())
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        return rule

    @staticmethod
    async def list_alerts(db: AsyncSession, status: Optional[AlertStatus] = None, severity: Optional[AlertSeverity] = None, limit: int = 100) -> List[AlertResponse]:
        stmt = select(Alert).options(selectinload(Alert.device)).order_by(desc(Alert.triggered_at)).limit(limit)
        if status:
            stmt = stmt.where(Alert.status == status)
        if severity:
            stmt = stmt.where(Alert.severity == severity)
        
        res = await db.execute(stmt)
        alerts = res.scalars().all()
        return [
            AlertResponse(
                id=a.id,
                rule_id=a.rule_id,
                device_id=a.device_id,
                device_hostname=a.device.hostname if a.device else "Unknown",
                message=a.message,
                metric_name=a.metric_name,
                metric_value=a.metric_value,
                severity=a.severity,
                status=a.status,
                acknowledged_by_id=a.acknowledged_by_id,
                acknowledged_at=a.acknowledged_at,
                triggered_at=a.triggered_at,
                resolved_at=a.resolved_at,
            )
            for a in alerts
        ]

    @staticmethod
    async def acknowledge_alerts(db: AsyncSession, req: AlertAcknowledgeRequest, user_id: Optional[int] = None) -> List[int]:
        stmt = select(Alert).where(Alert.id.in_(req.alert_ids))
        res = await db.execute(stmt)
        alerts = res.scalars().all()

        now = datetime.now(timezone.utc)
        for a in alerts:
            a.status = AlertStatus.ACKNOWLEDGED
            a.acknowledged_by_id = user_id
            a.acknowledged_at = now

        await db.commit()
        return [a.id for a in alerts]

    @staticmethod
    async def silence_device(db: AsyncSession, req: AlertSilenceRequest) -> AlertSuppression:
        now = datetime.now(timezone.utc)
        supp = AlertSuppression(
            device_id=req.device_id,
            reason=req.reason,
            starts_at=now,
            ends_at=now + timedelta(minutes=req.duration_minutes),
            is_active=True,
        )
        db.add(supp)
        await db.commit()
        await db.refresh(supp)
        return supp
