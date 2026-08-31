"""
Real-time WebSocket connection manager and event broadcasting bus.
"""

from typing import Dict, Set, Any, Optional
from fastapi import WebSocket
import json
import asyncio
import logging

logger = logging.getLogger("netops.websockets")


class ConnectionManager:
    def __init__(self):
        # Map of channel name -> set of connected WebSockets
        self.active_channels: Dict[str, Set[WebSocket]] = {
            "telemetry": set(),
            "alerts": set(),
            "discovery": set(),
            "topology": set(),
            "automation": set(),
            "incidents": set(),
            "all": set(),
        }
        self.client_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, channel: str = "all", client_id: Optional[str] = None):
        """Accept connection and register websocket to specified broadcast channels."""
        await websocket.accept()
        async with self._lock:
            if channel not in self.active_channels:
                self.active_channels[channel] = set()
            self.active_channels[channel].add(websocket)
            self.active_channels["all"].add(websocket)
            self.client_metadata[websocket] = {
                "channel": channel,
                "client_id": client_id,
            }
        logger.info(f"WebSocket client connected to channel '{channel}'. Total clients: {len(self.active_channels['all'])}")

    async def disconnect(self, websocket: WebSocket):
        """Unregister websocket and clean up active channels."""
        async with self._lock:
            for channel in self.active_channels.values():
                channel.discard(websocket)
            self.client_metadata.pop(websocket, None)
        logger.info("WebSocket client disconnected.")

    async def broadcast_channel(self, channel: str, message: Dict[str, Any]):
        """Broadcast payload to all clients subscribed to channel and 'all'."""
        payload = json.dumps(message)
        async with self._lock:
            subscribers = self.active_channels.get(channel, set()) | self.active_channels.get("all", set())
            targets = list(subscribers)

        for ws in targets:
            try:
                await ws.send_text(payload)
            except Exception as e:
                logger.warning(f"Error sending message to websocket: {e}")
                await self.disconnect(ws)

    async def broadcast_telemetry(self, device_id: int, metrics: Dict[str, Any]):
        """Specialized helper for telemetry metrics stream."""
        await self.broadcast_channel("telemetry", {
            "type": "TELEMETRY_UPDATE",
            "device_id": device_id,
            "data": metrics,
        })

    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Specialized helper for alert triggers."""
        await self.broadcast_channel("alerts", {
            "type": "ALERT_EVENT",
            "data": alert_data,
        })

    async def broadcast_discovery_progress(self, job_id: int, progress: int, message: str, discovered_count: int):
        """Specialized helper for discovery scanner progress."""
        await self.broadcast_channel("discovery", {
            "type": "DISCOVERY_PROGRESS",
            "job_id": job_id,
            "progress": progress,
            "message": message,
            "discovered_count": discovered_count,
        })

    async def broadcast_automation_step(self, run_id: int, node_id: str, status: str, output: Optional[str] = None):
        """Specialized helper for automation DAG execution steps."""
        await self.broadcast_channel("automation", {
            "type": "AUTOMATION_STEP",
            "run_id": run_id,
            "node_id": node_id,
            "status": status,
            "output": output,
        })


ws_manager = ConnectionManager()
