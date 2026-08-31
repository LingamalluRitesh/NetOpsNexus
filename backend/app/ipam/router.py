"""
FastAPI REST API router for IP Address Management (IPAM).
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission
from backend.app.rbac.permissions import Permission
from backend.app.ipam.schemas import (
    SubnetCreate, SubnetResponse, SubnetSplitRequest, SubnetMergeRequest,
    IpAddressCreate, IpAddressResponse, CidrCalculationRequest, CidrCalculationResponse,
    IpConflictResponse
)
from backend.app.ipam.service import IpamService
from backend.app.ipam.cidr_engine import CidrEngine

router = APIRouter(prefix="/ipam", tags=["IP Address Management (IPAM)"])


@router.get("/subnets", response_model=List[SubnetResponse])
async def list_subnets(
    vrf_id: Optional[int] = Query(None),
    site_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.IPAM_READ)),
) -> Any:
    """List all subnets with calculated utilization and IP counts."""
    return await IpamService.list_subnets(db, vrf_id=vrf_id, site_id=site_id)


@router.post("/subnets", response_model=SubnetResponse, status_code=status.HTTP_201_CREATED)
async def create_subnet(
    data: SubnetCreate,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.IPAM_WRITE)),
) -> Any:
    """Create a new IPv4 or IPv6 subnet."""
    return await IpamService.create_subnet(db, data)


@router.post("/subnets/split", response_model=List[SubnetResponse])
async def split_subnet(
    req: SubnetSplitRequest,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.IPAM_WRITE)),
) -> Any:
    """Split an existing subnet into smaller prefix blocks."""
    return await IpamService.split_subnet(db, req)


@router.post("/ips/allocate", response_model=IpAddressResponse, status_code=status.HTTP_201_CREATED)
async def allocate_ip(
    data: IpAddressCreate,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.IPAM_WRITE)),
) -> Any:
    """Allocate or reserve an IP address within a subnet."""
    return await IpamService.allocate_ip(db, data)


@router.delete("/ips/{ip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def release_ip(
    ip_id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.IPAM_WRITE)),
):
    """Release an allocated IP address back to available pool."""
    await IpamService.release_ip(db, ip_id)


@router.get("/conflicts", response_model=List[IpConflictResponse])
async def list_conflicts(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.IPAM_READ)),
) -> Any:
    """List all detected IP address collision conflicts."""
    return await IpamService.list_conflicts(db)


@router.post("/calculate-cidr", response_model=CidrCalculationResponse)
async def calculate_cidr(
    req: CidrCalculationRequest,
    _: Any = Depends(require_permission(Permission.IPAM_READ)),
) -> Any:
    """Calculate subnet parameters (netmask, usable range, hosts) from CIDR notation."""
    try:
        return CidrEngine.calculate_cidr(req.cidr)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
