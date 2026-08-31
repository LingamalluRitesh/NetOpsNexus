"""
FastAPI REST API router for PDF/CSV reports and data export.
"""

from typing import Any
from fastapi import APIRouter, Depends, Response
from fastapi.responses import Response, PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.dependencies import require_permission
from backend.app.rbac.permissions import Permission
from backend.app.reports.service import ReportsService

router = APIRouter(prefix="/reports", tags=["Reports & Export Hub"])


@router.get("/executive-summary/pdf")
async def download_executive_pdf(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.REPORTS_EXPORT)),
):
    """Download executive network operations PDF report."""
    pdf_bytes = await ReportsService.generate_executive_pdf(db)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=netops_executive_summary.pdf"},
    )


@router.get("/devices/csv")
async def download_devices_csv(
    db: AsyncSession = Depends(get_db),
    _: Any = Depends(require_permission(Permission.REPORTS_EXPORT)),
):
    """Export complete hardware device inventory in CSV format."""
    csv_text = await ReportsService.export_devices_csv(db)
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=netops_device_inventory.csv"},
    )
