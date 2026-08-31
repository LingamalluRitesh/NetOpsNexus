"""
FastAPI REST API router for Network Diagnostics Toolkit (Ping, Traceroute, DNS, Port Probe).
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission
from backend.app.rbac.permissions import Permission
from backend.app.diagnostics.schemas import (
    PingRequest, PingResponse, TracerouteRequest, TracerouteResponse,
    DnsLookupRequest, DnsLookupResponse, PortProbeRequest, PortProbeResponse
)
from backend.app.diagnostics.service import DiagnosticsService

router = APIRouter(prefix="/diagnostics", tags=["Diagnostics Toolkit"])


@router.post("/ping", response_model=PingResponse)
async def run_ping_test(
    req: PingRequest,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.MONITORING_READ)),
) -> Any:
    """Execute high-precision ICMP/TCP ping test."""
    return await DiagnosticsService.run_ping(db, req)


@router.post("/traceroute", response_model=TracerouteResponse)
async def run_traceroute_test(
    req: TracerouteRequest,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.MONITORING_READ)),
) -> Any:
    """Execute multi-hop path traceroute analysis."""
    return await DiagnosticsService.run_traceroute(db, req)


@router.post("/dns", response_model=DnsLookupResponse)
async def run_dns_lookup(
    req: DnsLookupRequest,
    _: Any = Depends(require_permission(Permission.MONITORING_READ)),
) -> Any:
    """Perform forward or reverse DNS resolution lookup."""
    return await DiagnosticsService.run_dns_lookup(req)


@router.post("/port-probe", response_model=PortProbeResponse)
async def run_port_probe(
    req: PortProbeRequest,
    _: Any = Depends(require_permission(Permission.MONITORING_READ)),
) -> Any:
    """Test TCP socket reachability on target host & port."""
    return await DiagnosticsService.run_port_probe(req)
