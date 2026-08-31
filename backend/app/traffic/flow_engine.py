"""
NetFlow / sFlow aggregation engine calculating Top Talkers (Source, Destination, App, Protocol).
"""

from typing import List, Dict, Any
from collections import defaultdict
from backend.app.traffic.models import TrafficFlowRecord
from backend.app.traffic.schemas import TopTalkersResponse, TopTalkerItem


class TrafficFlowEngine:
    @staticmethod
    def calculate_top_talkers(records: List[TrafficFlowRecord], window_hours: int = 24) -> TopTalkersResponse:
        """Aggregate flow records into ranked Top Talker statistics."""
        total_bytes = sum(r.bytes_count for r in records)
        if total_bytes == 0:
            total_bytes = 1  # Avoid division by zero

        src_agg = defaultdict(lambda: {"bytes": 0, "flows": 0})
        dst_agg = defaultdict(lambda: {"bytes": 0, "flows": 0})
        app_agg = defaultdict(lambda: {"bytes": 0, "flows": 0})
        proto_agg = defaultdict(lambda: {"bytes": 0, "flows": 0})

        for r in records:
            src_agg[r.src_ip]["bytes"] += r.bytes_count
            src_agg[r.src_ip]["flows"] += 1

            dst_agg[r.dst_ip]["bytes"] += r.bytes_count
            dst_agg[r.dst_ip]["flows"] += 1

            app_agg[r.application_name]["bytes"] += r.bytes_count
            app_agg[r.application_name]["flows"] += 1

            proto_agg[r.protocol]["bytes"] += r.bytes_count
            proto_agg[r.protocol]["flows"] += 1

        def _to_items(agg_dict: dict, top_k: int = 5) -> List[TopTalkerItem]:
            sorted_items = sorted(agg_dict.items(), key=lambda x: x[1]["bytes"], reverse=True)[:top_k]
            return [
                TopTalkerItem(
                    entity=k,
                    bytes_total=v["bytes"],
                    megabytes_total=round(v["bytes"] / (1024 * 1024), 2),
                    percentage=round((v["bytes"] / total_bytes) * 100.0, 1),
                    flows_count=v["flows"],
                )
                for k, v in sorted_items
            ]

        return TopTalkersResponse(
            time_window_hours=window_hours,
            total_volume_gigabytes=round(total_bytes / (1024 * 1024 * 1024), 3),
            top_sources=_to_items(src_agg),
            top_destinations=_to_items(dst_agg),
            top_applications=_to_items(app_agg),
            top_protocols=_to_items(proto_agg),
        )
