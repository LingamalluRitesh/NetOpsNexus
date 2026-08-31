"""
Pydantic schemas for Capacity Forecasting and Bandwidth / Memory Exhaustion Predictions.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date


class CapacityForecastItem(BaseModel):
    resource_type: str  # interface_bandwidth, device_cpu, device_memory, ipam_subnet
    resource_id: str
    resource_name: str
    current_utilization_pct: float
    daily_growth_rate_pct: float
    days_to_threshold_80: Optional[int] = None
    days_to_saturation_100: Optional[int] = None
    projected_exhaustion_date: Optional[date] = None
    urgency_level: str  # critical (<30 days), warning (30-90 days), normal (>90 days)
    recommendation: str


class CapacityOverviewResponse(BaseModel):
    total_resources_analyzed: int
    critical_saturation_count: int
    warning_saturation_count: int
    top_critical_forecasts: List[CapacityForecastItem]
    generated_at: datetime
