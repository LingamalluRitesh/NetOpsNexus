"""
Service layer for logging audit events and querying immutable compliance history.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.audit.models import AuditLog


class AuditService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        username: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return entry

    @staticmethod
    async def list_logs(
        db: AsyncSession,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditLog]:
        stmt = select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit)
        if resource_type:
            stmt = stmt.where(AuditLog.resource_type == resource_type)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        res = await db.execute(stmt)
        return list(res.scalars().all())
