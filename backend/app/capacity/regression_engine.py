"""
Linear Regression Capacity Growth Predictor estimating future saturation milestones.
"""

from typing import List, Tuple, Optional
from datetime import datetime, timezone, timedelta, date
import numpy as np
from backend.app.capacity.schemas import CapacityForecastItem


class CapacityRegressionEngine:
    @staticmethod
    def forecast_linear(
        resource_type: str,
        resource_id: str,
        resource_name: str,
        history_values: List[float],
        current_val: float,
        daily_growth_default: float = 0.25,
    ) -> CapacityForecastItem:
        """Fit linear regression line and project days to 80% and 100% capacity."""
        if len(history_values) >= 3:
            x = np.arange(len(history_values))
            y = np.array(history_values)
            slope, _ = np.polyfit(x, y, 1)
            growth_rate = max(0.01, float(slope))
        else:
            growth_rate = daily_growth_default

        rem_to_80 = max(0.0, 80.0 - current_val)
        rem_to_100 = max(0.0, 100.0 - current_val)

        days_80 = int(rem_to_80 / growth_rate) if growth_rate > 0 else 365
        days_100 = int(rem_to_100 / growth_rate) if growth_rate > 0 else 365

        exhaust_date = date.today() + timedelta(days=days_100)
        
        if days_80 <= 30 or current_val >= 80.0:
            urgency = "critical"
            rec = f"Immediate capacity upgrade required for {resource_name}. Saturation projected within {days_100} days."
        elif days_80 <= 90:
            urgency = "warning"
            rec = f"Plan budget and bandwidth provisioning for {resource_name} in next quarter's maintenance cycle."
        else:
            urgency = "normal"
            rec = f"Capacity healthy. Growth trend stable (+{growth_rate:.2f}%/day)."

        return CapacityForecastItem(
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            current_utilization_pct=round(current_val, 1),
            daily_growth_rate_pct=round(growth_rate, 2),
            days_to_threshold_80=days_80,
            days_to_saturation_100=days_100,
            projected_exhaustion_date=exhaust_date,
            urgency_level=urgency,
            recommendation=rec,
        )
