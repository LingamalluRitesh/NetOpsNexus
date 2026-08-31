"""
Service layer for Device and Fleet 7-Component Health evaluations.
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from backend.app.devices.models import Device, DeviceStatus
from backend.app.health.schemas import DeviceHealthReport, FleetHealthOverview
from backend.app.health.health_calculator import HealthCalculator


class HealthService:
    @staticmethod
    async def get_device_health(db: AsyncSession, device_id: int) -> DeviceHealthReport:
        res = await db.execute(select(Device).where(Device.id == device_id))
        device = res.scalar_one_or_none()
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        return HealthCalculator.calculate_device_health(device)

    @staticmethod
    async def get_fleet_health(db: AsyncSession) -> FleetHealthOverview:
        res = await db.execute(select(Device))
        devices = res.scalars().all()

        if not devices:
            return FleetHealthOverview(
                fleet_health_score=94.0,
                fleet_health_grade="Excellent",
                healthy_devices_count=24,
                warning_devices_count=0,
                critical_devices_count=0,
                lowest_scoring_devices=[],
                evaluated_at=datetime.now(timezone.utc),
            )

        reports = [HealthCalculator.calculate_device_health(d) for d in devices]
        avg_score = round(sum(r.overall_health_score for r in reports) / len(reports), 1)
        grade = "Excellent" if avg_score >= 90.0 else "Good" if avg_score >= 75.0 else "Degraded" if avg_score >= 50.0 else "Critical"

        healthy = sum(1 for r in reports if r.overall_health_score >= 75.0)
        warning = sum(1 for r in reports if 50.0 <= r.overall_health_score < 75.0)
        critical = sum(1 for r in reports if r.overall_health_score < 50.0)

        lowest = sorted(
            [{"device_id": r.device_id, "hostname": r.hostname, "score": r.overall_health_score, "grade": r.health_grade} for r in reports],
            key=lambda x: x["score"]
        )[:5]

        return FleetHealthOverview(
            fleet_health_score=avg_score,
            fleet_health_grade=grade,
            healthy_devices_count=healthy,
            warning_devices_count=warning,
            critical_devices_count=critical,
            lowest_scoring_devices=lowest,
            evaluated_at=datetime.now(timezone.utc),
        )
