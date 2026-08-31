"""
Unit tests for 7-Component Device and Fleet Health calculations.
"""

import pytest
from backend.app.devices.models import Device, DeviceType, DeviceStatus
from backend.app.health.health_calculator import HealthCalculator


def test_health_calculator_evaluation():
    device = Device(
        id=1,
        hostname="RTR-CORE-01",
        management_ip="10.100.0.1",
        device_type=DeviceType.CORE_ROUTER,
        vendor="Cisco",
        model="Catalyst 8500",
        os_type="cisco_ios",
        status=DeviceStatus.ONLINE,
        cpu_utilization=22.5,
        memory_utilization=38.0,
        uptime_seconds=864000,
    )

    report = HealthCalculator.calculate_device_health(device)
    assert report.device_id == 1
    assert report.overall_health_score >= 85.0
    assert report.health_grade in ["Excellent", "Good"]
    assert len(report.components) == 7
    assert any(c.name == "Reachability & Loss" for c in report.components)
    assert any(c.name == "CPU & Memory Utilization" for c in report.components)
    assert any(c.name == "BGP & Routing Stability" for c in report.components)
