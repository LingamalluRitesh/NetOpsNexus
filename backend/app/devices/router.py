"""
FastAPI REST API router for Devices, Interfaces, Sites, and CLI operations.
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission
from backend.app.rbac.permissions import Permission
from backend.app.devices.models import Device, DeviceStatus, DeviceType
from backend.app.devices.schemas import (
    DeviceCreate, DeviceUpdate, DeviceResponse, DeviceSummary,
    SiteCreate, SiteResponse, InterfaceResponse, RouteResponse,
    DeviceCliCommandRequest, DeviceCliCommandResponse
)
from backend.app.devices.service import DeviceService
from backend.app.devices.repository import SiteRepository
from backend.app.adapters.manager import AdapterManager

router = APIRouter(prefix="/devices", tags=["Device Inventory"])
site_router = APIRouter(prefix="/sites", tags=["Site Management"])


@router.get("", response_model=List[DeviceResponse])
async def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[DeviceStatus] = None,
    device_type: Optional[DeviceType] = None,
    site_id: Optional[int] = None,
    vendor: Optional[str] = None,
    query: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DEVICES_READ)),
) -> Any:
    """Retrieve list of network devices with multi-field filtering and pagination."""
    devices, total = await DeviceService.list_devices(
        db, skip=skip, limit=limit, status=status, device_type=device_type, site_id=site_id, vendor=vendor, query=query
    )
    return devices


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    data: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DEVICES_WRITE)),
) -> Any:
    """Register a new managed device and perform initial adapter discovery sync."""
    return await DeviceService.create_device(db, data)


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DEVICES_READ)),
) -> Any:
    """Retrieve complete device detail including interfaces and routing table."""
    return await DeviceService.get_device(db, device_id)


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: int,
    data: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DEVICES_WRITE)),
) -> Any:
    """Update device configuration and metadata."""
    return await DeviceService.update_device(db, device_id, data)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DEVICES_DELETE)),
):
    """Decommission and remove device from inventory."""
    await DeviceService.delete_device(db, device_id)


@router.post("/{device_id}/sync", response_model=DeviceResponse)
async def sync_device_telemetry(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DEVICES_WRITE)),
) -> Any:
    """Force an immediate telemetry poll and interface refresh from device adapter."""
    device = await DeviceService.get_device(db, device_id)
    return await DeviceService.sync_device_from_adapter(db, device)


@router.post("/{device_id}/cli", response_model=DeviceCliCommandResponse)
async def execute_cli(
    device_id: int,
    req: DeviceCliCommandRequest,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DEVICES_WRITE)),
) -> Any:
    """Execute raw CLI command on device and return terminal output."""
    return await DeviceService.execute_cli_command(db, device_id, req)


@router.post("/{device_id}/ping")
async def ping_device(
    device_id: int,
    count: int = Query(5, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DIAGNOSTICS_RUN)),
) -> Any:
    """Execute diagnostic ICMP ping against device."""
    device = await DeviceService.get_device(db, device_id)
    adapter = AdapterManager.get_adapter(device.management_ip)
    res = await adapter.ping(count=count)
    return res


# --- Site Endpoints ---
@site_router.get("", response_model=List[SiteResponse])
async def list_sites(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DEVICES_READ)),
) -> Any:
    """List all enterprise physical sites and data centers."""
    return await SiteRepository.list_sites(db)


@site_router.post("", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    data: SiteCreate,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.DEVICES_WRITE)),
) -> Any:
    """Create a new physical site facility."""
    return await SiteRepository.create(db, data)
