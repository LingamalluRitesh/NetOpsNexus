"""
Service layer for executive reports, CSV data exports, and PDF generation.
"""

from typing import List, Dict, Any
import io
import csv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.devices.models import Device
from backend.app.incidents.models import Incident
from backend.app.health.service import HealthService
from backend.app.security.service import SecurityService
from backend.app.incidents.service import IncidentService
from backend.app.reports.pdf_generator import PdfReportGenerator


class ReportsService:
    @staticmethod
    async def generate_executive_pdf(db: AsyncSession) -> bytes:
        fleet_health = await HealthService.get_fleet_health(db)
        sec_overview = await SecurityService.get_security_overview(db)
        mttr_data = await IncidentService.get_mttr_analytics(db)

        payload = {
            "total_devices": fleet_health.healthy_devices_count + fleet_health.warning_devices_count + fleet_health.critical_devices_count,
            "health_score": fleet_health.fleet_health_score,
            "security_score": sec_overview.overall_fleet_score,
            "mttr_min": mttr_data.mean_time_to_resolution_minutes,
            "active_p1_p2": mttr_data.p1_incidents_count + mttr_data.p2_incidents_count,
        }
        return PdfReportGenerator.generate_executive_summary_pdf(payload)

    @staticmethod
    async def export_devices_csv(db: AsyncSession) -> str:
        res = await db.execute(select(Device).options(selectinload(Device.site)))
        devices = res.scalars().all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Hostname", "Management IP", "Device Type", "Vendor", "Model", "OS Type", "Status", "Site"])

        for d in devices:
            site_name = d.site.name if d.site else "N/A"
            writer.writerow([d.id, d.hostname, d.management_ip, d.device_type.value, d.vendor, d.model, d.os_type, d.status.value, site_name])

        return output.getvalue()
