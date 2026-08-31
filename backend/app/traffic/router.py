"""
FastAPI REST API router for NetFlow / sFlow ingestion and Top Talkers analysis.
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission
from backend.app.rbac.permissions import Permission
from backend.app.traffic.schemas import FlowRecordCreate, TopTalkersResponse
from backend.app.traffic.service import TrafficService

router = APIRouter(prefix="/traffic", tags=["Traffic Intelligence"])


@router.get("/top-talkers", response_model=TopTalkersResponse)
async def get_top_talkers(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.TRAFFIC_READ)),
) -> Any:
    """Retrieve bandwidth Top Talkers by Source, Destination, Application, and Protocol."""
    return await TrafficService.get_top_talkers(db, hours=hours)


@router.post("/flows/ingest")
async def ingest_traffic_flows(
    flows: List[FlowRecordCreate],
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.TRAFFIC_WRITE)),
) -> Any:
    """Ingest a batch of NetFlow v5/v9 or sFlow parsed records."""
    count = await TrafficService.ingest_flows(db, flows)
    return {"message": f"Successfully ingested {count} flow records"}
