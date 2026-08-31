"""
Data access repository layer for Device entities, interfaces, routing tables, and sites.
"""

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, delete
from sqlalchemy.orm import selectinload
from backend.app.devices.models import Device, NetworkInterface, RoutingTableEntry, Site, Rack, Vlan, DeviceStatus, DeviceType
from backend.app.devices.schemas import DeviceCreate, DeviceUpdate, SiteCreate, InterfaceCreate, RouteCreate, VlanCreate


class DeviceRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, device_id: int) -> Optional[Device]:
        """Fetch single device with all eager relationships loaded."""
        stmt = (
            select(Device)
            .options(
                selectinload(Device.site),
                selectinload(Device.rack),
                selectinload(Device.interfaces),
                selectinload(Device.routes),
            )
            .where(Device.id == device_id)
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def get_by_hostname(db: AsyncSession, hostname: str) -> Optional[Device]:
        stmt = select(Device).where(Device.hostname == hostname)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def get_by_ip(db: AsyncSession, ip_address: str) -> Optional[Device]:
        stmt = select(Device).where(Device.management_ip == ip_address)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def list_devices(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[DeviceStatus] = None,
        device_type: Optional[DeviceType] = None,
        site_id: Optional[int] = None,
        vendor: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Tuple[List[Device], int]:
        """List devices matching multi-criteria filter predicates with total count."""
        filters = []
        if status:
            filters.append(Device.status == status)
        if device_type:
            filters.append(Device.device_type == device_type)
        if site_id:
            filters.append(Device.site_id == site_id)
        if vendor:
            filters.append(Device.vendor.ilike(f"%{vendor}%"))
        if query:
            filters.append(
                or_(
                    Device.hostname.ilike(f"%{query}%"),
                    Device.management_ip.ilike(f"%{query}%"),
                    Device.model.ilike(f"%{query}%"),
                )
            )

        # Count total
        count_stmt = select(func.count(Device.id))
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        count_res = await db.execute(count_stmt)
        total = count_res.scalar_one()

        # Query page
        stmt = (
            select(Device)
            .options(
                selectinload(Device.site),
                selectinload(Device.interfaces),
                selectinload(Device.routes),
            )
            .order_by(Device.hostname)
            .offset(skip)
            .limit(limit)
        )
        if filters:
            stmt = stmt.where(and_(*filters))

        res = await db.execute(stmt)
        return list(res.scalars().all()), total

    @staticmethod
    async def create(db: AsyncSession, data: DeviceCreate) -> Device:
        device = Device(
            hostname=data.hostname,
            management_ip=data.management_ip,
            device_type=data.device_type,
            vendor=data.vendor,
            model=data.model,
            os_type=data.os_type,
            os_version=data.os_version,
            serial_number=data.serial_number,
            mac_address=data.mac_address,
            site_id=data.site_id,
            rack_id=data.rack_id,
            rack_unit=data.rack_unit,
            status=data.status,
            snmp_community=data.snmp_community,
            snmp_version=data.snmp_version,
            ssh_port=data.ssh_port,
            is_managed=data.is_managed,
            tags=data.tags or {},
        )
        db.add(device)
        await db.flush()
        await db.refresh(device, ["site", "interfaces", "routes"])
        return device

    @staticmethod
    async def update(db: AsyncSession, device: Device, data: DeviceUpdate) -> Device:
        update_dict = data.model_dump(exclude_unset=True)
        for k, v in update_dict.items():
            setattr(device, k, v)
        await db.flush()
        return device

    @staticmethod
    async def delete(db: AsyncSession, device: Device):
        await db.delete(device)
        await db.flush()


class SiteRepository:
    @staticmethod
    async def list_sites(db: AsyncSession) -> List[Site]:
        stmt = select(Site).options(selectinload(Site.devices), selectinload(Site.vlans)).order_by(Site.name)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, site_id: int) -> Optional[Site]:
        stmt = select(Site).options(selectinload(Site.racks), selectinload(Site.devices)).where(Site.id == site_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: SiteCreate) -> Site:
        site = Site(**data.model_dump())
        db.add(site)
        await db.flush()
        return site
