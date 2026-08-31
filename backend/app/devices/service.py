"""
Domain business service for Device Inventory, Interface synchronization, and CLI execution.
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.devices.models import Device, NetworkInterface, RoutingTableEntry, Site, Rack, Vlan, DeviceStatus
from backend.app.devices.schemas import (
    DeviceCreate, DeviceUpdate, InterfaceCreate, InterfaceUpdate, RouteCreate,
    DeviceCliCommandRequest, DeviceCliCommandResponse
)
from backend.app.devices.repository import DeviceRepository, SiteRepository
from backend.app.adapters.manager import AdapterManager


class DeviceService:
    @staticmethod
    async def list_devices(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        device_type: Optional[str] = None,
        site_id: Optional[int] = None,
        vendor: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Tuple[List[Device], int]:
        return await DeviceRepository.list_devices(
            db, skip=skip, limit=limit, status=status, device_type=device_type, site_id=site_id, vendor=vendor, query=query
        )

    @staticmethod
    async def get_device(db: AsyncSession, device_id: int) -> Device:
        device = await DeviceRepository.get_by_id(db, device_id)
        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Device with ID {device_id} not found")
        return device

    @staticmethod
    async def create_device(db: AsyncSession, data: DeviceCreate) -> Device:
        # Check duplicate hostname or IP
        existing = await DeviceRepository.get_by_hostname(db, data.hostname)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Device with hostname '{data.hostname}' already exists")

        device = await DeviceRepository.create(db, data)
        # Perform initial sync from adapter
        await DeviceService.sync_device_from_adapter(db, device)
        return device

    @staticmethod
    async def update_device(db: AsyncSession, device_id: int, data: DeviceUpdate) -> Device:
        device = await DeviceService.get_device(db, device_id)
        return await DeviceRepository.update(db, device, data)

    @staticmethod
    async def delete_device(db: AsyncSession, device_id: int):
        device = await DeviceService.get_device(db, device_id)
        await DeviceRepository.delete(db, device)

    @staticmethod
    async def sync_device_from_adapter(db: AsyncSession, device: Device) -> Device:
        """Poll device adapter and synchronize system telemetry, interfaces, and routes."""
        adapter = AdapterManager.get_adapter(
            host_or_ip=device.management_ip,
            snmp_community=device.snmp_community,
            ssh_port=device.ssh_port,
        )

        try:
            # 1. Update system info
            sys_info = await adapter.get_system_info()
            device.uptime_seconds = sys_info.uptime_seconds
            device.cpu_utilization = sys_info.cpu_percent
            device.memory_utilization = sys_info.memory_percent
            device.temperature_celsius = sys_info.temperature_c
            if sys_info.mac_address and not device.mac_address:
                device.mac_address = sys_info.mac_address
            device.last_seen = datetime.now(timezone.utc)
            device.status = DeviceStatus.ONLINE

            # 2. Synchronize interfaces
            iface_infos = await adapter.get_interfaces()
            existing_ifaces = {i.name: i for i in device.interfaces}

            for if_info in iface_infos:
                if if_info.name in existing_ifaces:
                    db_if = existing_ifaces[if_info.name]
                    db_if.speed_mbps = if_info.speed_mbps
                    db_if.admin_status = if_info.admin_status
                    db_if.oper_status = if_info.oper_status
                    db_if.rx_bps = if_info.rx_bps
                    db_if.tx_bps = if_info.tx_bps
                    db_if.rx_pps = if_info.rx_pps
                    db_if.tx_pps = if_info.tx_pps
                    db_if.rx_errors = if_info.rx_errors
                    db_if.tx_errors = if_info.tx_errors
                    db_if.rx_drops = if_info.rx_drops
                    db_if.tx_drops = if_info.tx_drops
                    db_if.last_change = datetime.now(timezone.utc)
                else:
                    new_if = NetworkInterface(
                        device_id=device.id,
                        name=if_info.name,
                        description=if_info.description,
                        if_index=if_info.if_index,
                        mac_address=if_info.mac_address,
                        ip_address=if_info.ip_address,
                        subnet_mask=if_info.subnet_mask,
                        speed_mbps=if_info.speed_mbps,
                        duplex=if_info.duplex,
                        mtu=if_info.mtu,
                        admin_status=if_info.admin_status,
                        oper_status=if_info.oper_status,
                        is_trunk=if_info.is_trunk,
                        rx_bps=if_info.rx_bps,
                        tx_bps=if_info.tx_bps,
                        rx_pps=if_info.rx_pps,
                        tx_pps=if_info.tx_pps,
                        rx_errors=if_info.rx_errors,
                        tx_errors=if_info.tx_errors,
                        rx_drops=if_info.rx_drops,
                        tx_drops=if_info.tx_drops,
                        last_change=datetime.now(timezone.utc),
                    )
                    db.add(new_if)

            # 3. Synchronize routes
            route_infos = await adapter.get_routes()
            await db.execute(delete(RoutingTableEntry).where(RoutingTableEntry.device_id == device.id))
            for r_info in route_infos:
                new_rt = RoutingTableEntry(
                    device_id=device.id,
                    destination_prefix=r_info.destination_prefix,
                    next_hop=r_info.next_hop,
                    protocol=r_info.protocol,
                    metric=r_info.metric,
                    admin_distance=r_info.admin_distance,
                    outgoing_interface=r_info.outgoing_interface,
                    is_active=True,
                )
                db.add(new_rt)

            await db.commit()
            await db.refresh(device, ["interfaces", "routes", "site"])
            return device

        except Exception as e:
            device.status = DeviceStatus.CRITICAL
            await db.commit()
            raise HTTPException(status_code=500, detail=f"Failed to sync with device adapter: {str(e)}")

    @staticmethod
    async def execute_cli_command(db: AsyncSession, device_id: int, req: DeviceCliCommandRequest) -> DeviceCliCommandResponse:
        """Execute interactive CLI command on device via active adapter."""
        device = await DeviceService.get_device(db, device_id)
        adapter = AdapterManager.get_adapter(
            host_or_ip=device.management_ip,
            ssh_port=device.ssh_port,
        )

        result = await adapter.execute_command(req.command)
        return DeviceCliCommandResponse(
            device_id=device.id,
            hostname=device.hostname,
            command=req.command,
            output=result.output,
            execution_time_ms=result.execution_time_ms,
            status=result.status,
        )
