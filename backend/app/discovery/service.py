"""
Service layer for managing Discovery jobs, triggering background scans, and importing to inventory.
"""

from typing import List, Optional, Tuple
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.discovery.models import DiscoveryJob, DiscoveredDevice, JobStatus
from backend.app.discovery.schemas import DiscoveryScanConfig, ImportDiscoveredRequest
from backend.app.discovery.engine import DiscoveryEngine
from backend.app.devices.models import Device, DeviceType, DeviceStatus
from backend.app.devices.schemas import DeviceCreate
from backend.app.devices.service import DeviceService


class DiscoveryService:
    @staticmethod
    async def create_and_start_job(db: AsyncSession, config: DiscoveryScanConfig) -> DiscoveryJob:
        """Create a new discovery job record and launch background scanner task."""
        job = DiscoveryJob(
            name=config.name,
            target_cidr=config.target_cidr,
            scan_type=config.scan_type,
            status=JobStatus.QUEUED,
            snmp_community=config.snmp_community,
            progress_percent=0,
            discovered_count=0,
            failed_count=0,
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        # Run pipeline inline or in task queue
        asyncio.create_task(DiscoveryEngine.run_discovery_pipeline(db, job))
        return job

    @staticmethod
    async def list_jobs(db: AsyncSession, limit: int = 50) -> List[DiscoveryJob]:
        stmt = select(DiscoveryJob).options(selectinload(DiscoveryJob.discovered_devices)).order_by(desc(DiscoveryJob.created_at)).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_job(db: AsyncSession, job_id: int) -> DiscoveryJob:
        stmt = select(DiscoveryJob).options(selectinload(DiscoveryJob.discovered_devices)).where(DiscoveryJob.id == job_id)
        res = await db.execute(stmt)
        job = res.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Discovery job {job_id} not found")
        return job

    @staticmethod
    async def import_devices(db: AsyncSession, req: ImportDiscoveredRequest) -> List[Device]:
        """Import selected discovered devices into core managed device inventory."""
        imported_devices = []
        stmt = select(DiscoveredDevice).where(DiscoveredDevice.id.in_(req.device_ids))
        res = await db.execute(stmt)
        discovered_list = res.scalars().all()

        for d in discovered_list:
            if d.is_imported:
                continue

            # Determine device type
            dtype = DeviceType.ACCESS_SWITCH
            if "router" in (d.model or "").lower() or "rtr" in (d.hostname or "").lower():
                dtype = DeviceType.CORE_ROUTER
            elif "firewall" in (d.model or "").lower() or "fw" in (d.hostname or "").lower():
                dtype = DeviceType.FIREWALL
            elif "ap" in (d.model or "").lower() or "wap" in (d.hostname or "").lower():
                dtype = DeviceType.WIRELESS_AP

            create_schema = DeviceCreate(
                hostname=d.hostname or f"node-{d.ip_address.replace('.', '-')}",
                management_ip=d.ip_address,
                device_type=dtype,
                vendor=d.vendor or "Generic",
                model=d.model or "Standard Network Device",
                os_type=d.os_detected or "cisco_ios",
                os_version="1.0",
                mac_address=d.mac_address,
                site_id=req.target_site_id,
                status=DeviceStatus.ONLINE,
            )
            try:
                dev = await DeviceService.create_device(db, create_schema)
                d.is_imported = True
                imported_devices.append(dev)
            except Exception:
                # If device already exists, mark as imported
                d.is_imported = True

        await db.commit()
        return imported_devices
