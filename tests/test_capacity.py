"""
Unit tests for Capacity Regression Forecasting.
"""

import pytest
from backend.app.capacity.regression_engine import CapacityRegressionEngine


def test_capacity_regression_forecast():
    # Resource growing from 50% -> 60% -> 70%
    history = [50.0, 60.0, 70.0]
    forecast = CapacityRegressionEngine.forecast_linear(
        resource_type="interface_bandwidth",
        resource_id="1_HundredGigE1/0/1",
        resource_name="CORE Uplink",
        history_values=history,
        current_val=70.0,
    )
    assert forecast.current_utilization_pct == 70.0
    assert forecast.daily_growth_rate_pct >= 9.0  # Slope is ~10%/unit
    assert forecast.days_to_threshold_80 <= 5
    assert forecast.days_to_saturation_100 <= 10
    assert forecast.urgency_level == "critical"
