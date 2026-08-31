"""
Pydantic schemas for the Audit Log trail.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    username: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    timestamp: datetime
