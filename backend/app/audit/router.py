"""
FastAPI REST API router for Immutable Audit Trail inspection.
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission
from backend.app.rbac.permissions import Permission
from backend.app.audit.schemas import AuditLogResponse
from backend.app.audit.service import AuditService

router = APIRouter(prefix="/audit", tags=["Compliance & Audit Trail"])


@router.get("/logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    resource_type: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.AUDIT_READ)),
) -> Any:
    """Retrieve immutable record of all administrative network operations."""
    return await AuditService.list_logs(db, resource_type=resource_type, action=action, limit=limit)
