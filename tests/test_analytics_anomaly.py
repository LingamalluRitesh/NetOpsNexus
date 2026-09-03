"""
Unit tests for Telemetry Downsampling and Anomaly Detection Engine.
"""

from datetime import datetime, timezone, timedelta
import pytest
from backend.app.monitoring.analytics.downsampler import TelemetryDownsampler
from backend.app.monitoring.analytics.anomaly_detector import TelemetryAnomalyDetector


def test_telemetry_downsampler():
    base_time = datetime(2026, 8, 30, 12, 0, 0, tzinfo=timezone.utc)
    points = []
    # 60 points spanning 1 hour (one per minute)
    for m in range(60):
        dt = base_time + timedelta(minutes=m)
        val = 20.0 + (m % 10) * 2.0  # 20.0 to 38.0
        points.append((dt, val))

    # Downsample into 5-minute buckets (300 seconds)
    buckets = TelemetryDownsampler.aggregate_points(points, bucket_interval_seconds=300)
    assert len(buckets) == 12  # 60 mins / 5 mins = 12 buckets

    b0 = buckets[0]
    assert b0.sample_count == 5
    assert b0.min_val <= b0.mean_val <= b0.max_val
    assert b0.p95_val >= b0.mean_val


def test_telemetry_anomaly_detector():
    base_time = datetime(2026, 8, 30, 12, 0, 0, tzinfo=timezone.utc)
    # 25 steady points + 1 extreme outlier
    points = []
    for m in range(25):
        points.append((base_time + timedelta(minutes=m), 30.0 + (m % 3)))

    # Extreme spike to 99% CPU
    points.append((base_time + timedelta(minutes=25), 99.0))

    results = TelemetryAnomalyDetector.detect_zscore_anomalies(points, z_threshold=2.5)
    assert len(results) == 26

    # Normal points
    assert not results[10].is_anomaly
    assert results[10].severity == "INFO"

    # Outlier point
    outlier = results[-1]
    assert outlier.is_anomaly
    assert outlier.severity == "CRITICAL"
    assert "Extreme deviation" in outlier.reason


def test_interface_flapping_detection():
    base_time = datetime.now(timezone.utc)
    transitions = [
        (base_time - timedelta(seconds=240), "UP"),
        (base_time - timedelta(seconds=200), "DOWN"),
        (base_time - timedelta(seconds=160), "UP"),
        (base_time - timedelta(seconds=100), "DOWN"),
        (base_time - timedelta(seconds=40), "UP"),
    ]
    is_flapping = TelemetryAnomalyDetector.detect_interface_flapping(transitions, flaps_threshold=3, window_seconds=300)
    assert is_flapping is True
