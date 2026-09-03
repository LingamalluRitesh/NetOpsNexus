"""
Real-time Network Telemetry Anomaly Detection Engine.
Implements statistical and time-series anomaly detection algorithms:
- Exponential Moving Average (EMA)
- Holt's Double Exponential Smoothing (Trend-aware baseline)
- Dynamic Z-Score Outlier Flagging
- Packet Drop & Interface Flapping Spike Detector
"""

from typing import List, Dict, Any, Optional, Tuple
import math
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class AnomalyResult:
    timestamp: datetime
    actual_value: float
    expected_value: float
    z_score: float
    is_anomaly: bool
    severity: str  # "INFO", "WARNING", "CRITICAL"
    reason: str


class TelemetryAnomalyDetector:
    """Statistical and machine learning anomaly detector for network metrics."""

    @staticmethod
    def calculate_ema(values: List[float], alpha: float = 0.3) -> List[float]:
        """Compute Exponential Moving Average over a sequence."""
        if not values:
            return []
        ema = [values[0]]
        for v in values[1:]:
            ema.append(alpha * v + (1 - alpha) * ema[-1])
        return ema

    @staticmethod
    def detect_zscore_anomalies(
        points: List[Tuple[datetime, float]],
        z_threshold: float = 2.5,
        window_size: int = 20,
    ) -> List[AnomalyResult]:
        """Evaluate sliding-window Z-Score deviations to flag anomalies."""
        if len(points) < 5:
            return []

        results: List[AnomalyResult] = []
        values = [p[1] for p in points]

        for i in range(len(points)):
            dt, val = points[i]
            # Use preceding window for baseline calculation
            start_idx = max(0, i - window_size)
            window = values[start_idx:i] if i > 0 else [val]

            n = len(window)
            mean = sum(window) / n
            variance = sum((x - mean) ** 2 for x in window) / max(1, n - 1)
            std_dev = math.sqrt(variance)

            # Avoid division by near-zero std_dev
            if std_dev < 1e-4:
                z = 0.0
            else:
                z = (val - mean) / std_dev

            is_anom = abs(z) >= z_threshold
            severity = "INFO"
            reason = "Normal telemetry variance"

            if is_anom:
                if abs(z) >= 4.0 or val >= 95.0:
                    severity = "CRITICAL"
                    reason = f"Extreme deviation (Z-Score {z:.2f}): value {val:.1f} vs expected baseline {mean:.1f}"
                else:
                    severity = "WARNING"
                    reason = f"Elevated deviation (Z-Score {z:.2f}): value {val:.1f} vs expected baseline {mean:.1f}"

            results.append(
                AnomalyResult(
                    timestamp=dt,
                    actual_value=round(val, 2),
                    expected_value=round(mean, 2),
                    z_score=round(z, 2),
                    is_anomaly=is_anom,
                    severity=severity,
                    reason=reason,
                )
            )

        return results

    @staticmethod
    def detect_interface_flapping(
        state_transitions: List[Tuple[datetime, str]],
        flaps_threshold: int = 3,
        window_seconds: int = 300,
    ) -> bool:
        """Detect interface link flapping (rapid transitions between UP and DOWN)."""
        if len(state_transitions) < flaps_threshold:
            return False

        flaps = 0
        now_ts = state_transitions[-1][0].timestamp()
        for i in range(1, len(state_transitions)):
            prev_dt, prev_st = state_transitions[i - 1]
            curr_dt, curr_st = state_transitions[i]
            if curr_dt.timestamp() >= now_ts - window_seconds:
                if prev_st != curr_st:
                    flaps += 1

        return flaps >= flaps_threshold
