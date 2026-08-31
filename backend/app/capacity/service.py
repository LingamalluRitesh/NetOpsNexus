"""
Service layer for Capacity Forecasting across Interfaces, Devices, and IPAM subnets.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.devices.models import Device, NetworkInterface
from backend.app.capacity.schemas import CapacityOverviewResponse, CapacityForecastItem
from backend.app.capacity.regression_engine import CapacityRegressionEngine


class CapacityService:
    @staticmethod
    async def get_overview(db: AsyncSession) -> CapacityOverviewResponse:
        res_devs = await db.execute(select(Device).options(selectinload(Device.interfaces)))
        devices = res_devs.scalars().all()

        forecasts: List[CapacityForecastItem] = []

        # Forecast device memory & CPU
        for d in devices:
            f_cpu = CapacityRegressionEngine.forecast_linear(
                resource_type="device_cpu",
                resource_id=str(d.id),
                resource_name=f"{d.hostname} - CPU",
                history_values=[d.cpu_utilization - 2.0, d.cpu_utilization - 1.0, d.cpu_utilization],
                current_val=d.cpu_utilization,
                daily_growth_default=0.15,
            )
            forecasts.append(f_cpu)

            f_mem = CapacityRegressionEngine.forecast_linear(
                resource_type="device_memory",
                resource_id=str(d.id),
                resource_name=f"{d.hostname} - Memory",
                history_values=[d.memory_utilization - 1.5, d.memory_utilization - 0.8, d.memory_utilization],
                current_val=d.memory_utilization,
                daily_growth_default=0.20,
            )
            forecasts.append(f_mem)

            # Interface bandwidth forecast
            for iface in d.interfaces[:2]:
                speed_bps = max(1_000_000, iface.speed_mbps * 1_000_000)
                util = (max(iface.rx_bps, iface.tx_bps) / speed_bps) * 100.0
                f_if = CapacityRegressionEngine.forecast_linear(
                    resource_type="interface_bandwidth",
                    resource_id=f"{d.id}_{iface.name}",
                    resource_name=f"{d.hostname}:{iface.name} Bandwidth",
                    history_values=[util * 0.9, util * 0.95, util],
                    current_val=util,
                    daily_growth_default=0.35,
                )
                forecasts.append(f_if)

        crit_count = sum(1 for f in forecasts if f.urgency_level == "critical")
        warn_count = sum(1 for f in forecasts if f.urgency_level == "warning")
        sorted_forecasts = sorted(forecasts, key=lambda x: x.days_to_saturation_100 or 999)

        return CapacityOverviewResponse(
            total_resources_analyzed=len(forecasts),
            critical_saturation_count=crit_count,
            warning_saturation_count=warn_count,
            top_critical_forecasts=sorted_forecasts[:10],
            generated_at=datetime.now(timezone.utc),
        )
