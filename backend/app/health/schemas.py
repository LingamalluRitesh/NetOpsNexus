"""
Pydantic schemas for the 7-Component Device and Fleet Health Engine.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class HealthComponentBreakdown(BaseModel):
    name: str  # Reachability, CPU & Memory, Error Rates, BGP & Routing, Config Drift, Security Posture, Link Flapping
    weight_pct: int
    score_earned: float
    max_score: float
    status: str  # optimal, warning, critical
    details: str


class DeviceHealthReport(BaseModel):
    device_id: int
    hostname: str
    overall_health_score: float  # 0 to 100
    health_grade: str  # Excellent (90-100), Good (75-89), Degraded (50-74), Critical (<50)
    components: List[HealthComponentBreakdown]
    evaluated_at: datetime


class FleetHealthOverview(BaseModel):
    fleet_health_score: float
    fleet_health_grade: str
    healthy_devices_count: int
    warning_devices_count: int
    critical_devices_count: int
    lowest_scoring_devices: List[Dict[str, Any]]
    evaluated_at: datetime
