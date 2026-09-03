"""
Time-Series Telemetry Downsampling and Aggregation Engine.
Computes multi-resolution metric rollups:
- 1-minute, 5-minute, 1-hour, 1-day buckets
- Aggregates: Min, Max, Mean, P95, P99, Standard Deviation, and Rate of Change
"""

from typing import List, Dict, Any, Optional, Tuple
import math
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass


@dataclass
class MetricBucket:
    timestamp_bucket: datetime
    sample_count: int
    min_val: float
    max_val: float
    mean_val: float
    p95_val: float
    p99_val: float
    std_dev: float
    rate_of_change: float


class TelemetryDownsampler:
    """Multi-resolution metric bucket aggregator."""

    @staticmethod
    def aggregate_points(points: List[Tuple[datetime, float]], bucket_interval_seconds: int = 300) -> List[MetricBucket]:
        """Aggregate raw timestamp-value tuples into uniform fixed-width time buckets."""
        if not points:
            return []

        # Sort points by timestamp
        sorted_points = sorted(points, key=lambda x: x[0])
        buckets: Dict[int, List[float]] = {}

        for dt, val in sorted_points:
            epoch = int(dt.timestamp())
            bucket_key = (epoch // bucket_interval_seconds) * bucket_interval_seconds
            if bucket_key not in buckets:
                buckets[bucket_key] = []
            buckets[bucket_key].append(val)

        results: List[MetricBucket] = []
        prev_mean = None

        for b_key in sorted(buckets.keys()):
            vals = buckets[b_key]
            n = len(vals)
            if n == 0:
                continue

            sorted_vals = sorted(vals)
            min_v = sorted_vals[0]
            max_v = sorted_vals[-1]
            mean_v = sum(vals) / n

            # Percentiles
            p95_idx = min(n - 1, int(math.ceil(0.95 * n)) - 1)
            p99_idx = min(n - 1, int(math.ceil(0.99 * n)) - 1)
            p95_v = sorted_vals[p95_idx]
            p99_v = sorted_vals[p99_idx]

            # Standard deviation
            variance = sum((x - mean_v) ** 2 for x in vals) / max(1, n - 1)
            std_dev = math.sqrt(variance)

            # Rate of change relative to previous bucket
            roc = 0.0
            if prev_mean is not None and prev_mean > 0:
                roc = ((mean_v - prev_mean) / prev_mean) * 100.0
            prev_mean = mean_v

            bucket_dt = datetime.fromtimestamp(b_key, tz=timezone.utc)
            results.append(
                MetricBucket(
                    timestamp_bucket=bucket_dt,
                    sample_count=n,
                    min_val=round(min_v, 2),
                    max_val=round(max_v, 2),
                    mean_val=round(mean_v, 2),
                    p95_val=round(p95_v, 2),
                    p99_val=round(p99_v, 2),
                    std_dev=round(std_dev, 2),
                    rate_of_change=round(roc, 2),
                )
            )

        return results
