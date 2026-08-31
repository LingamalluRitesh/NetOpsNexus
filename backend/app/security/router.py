"""
FastAPI REST API router for Security Audits, CIS Compliance, and ACL Shadow Analysis.
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission
from backend.app.rbac.permissions import Permission
from backend.app.security.schemas import (
    SecurityAuditResponse, SecurityScoreOverview, AclRuleBase,
    AclShadowAnalysisResponse, RogueDeviceResponse
)
from backend.app.security.service import SecurityService

router = APIRouter(prefix="/security", tags=["Security & Compliance"])


@router.get("/overview", response_model=SecurityScoreOverview)
async def get_security_overview(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.SECURITY_READ)),
) -> Any:
    """Retrieve enterprise network security posture score and CIS benchmark metrics."""
    return await SecurityService.get_security_overview(db)


@router.post("/devices/{device_id}/audit", response_model=SecurityAuditResponse)
async def run_device_security_audit(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.SECURITY_WRITE)),
) -> Any:
    """Run full CIS hardening security benchmark audit on target device."""
    return await SecurityService.run_device_audit(db, device_id)


@router.post("/acl/analyze", response_model=AclShadowAnalysisResponse)
async def analyze_acl_shadowing(
    device_id: int,
    acl_name: str,
    rules: List[AclRuleBase],
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.SECURITY_READ)),
) -> Any:
    """Detect shadowed, redundant, and unreachable access-list rules."""
    return await SecurityService.analyze_acl(db, device_id=device_id, acl_name=acl_name, rules_in=rules)


@router.get("/rogue-devices", response_model=List[RogueDeviceResponse])
async def list_rogue_devices(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.SECURITY_READ)),
) -> Any:
    """List rogue and unapproved MAC/IP address detections."""
    return await SecurityService.list_rogue_devices(db)
