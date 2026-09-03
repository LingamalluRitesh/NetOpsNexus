"""
Telemetry collector polling device adapters, saving time-series metric snapshots,
and broadcasting real-time WebSocket metrics to connected frontend dashboards.
"""

from typing import List, Dict, Any
import asyncio
import time
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.database import AsyncSessionLocal
from backend.app.devices.models import Device, NetworkInterface, DeviceStatus
from backend.app.monitoring.models import DeviceMetric, InterfaceMetric, BgpPeerMetric
from backend.app.adapters.manager import AdapterManager
from backend.app.websocket_manager import ws_manager


class TelemetryCollector:
    @staticmethod
    async def collect_single_device(db: AsyncSession, device: Device):
        """Poll telemetry from a single device adapter and record time-series entries."""
        adapter = AdapterManager.get_adapter(
            host_or_ip=device.management_ip,
            snmp_community=device.snmp_community,
            ssh_port=device.ssh_port,
        )

        try:
            # 1. Ping & Reachability
            ping_res = await adapter.ping(count=2, timeout_sec=0.8)
            sys_info = await adapter.get_system_info()

            # Record device metric
            dev_metric = DeviceMetric(
                device_id=device.id,
                cpu_utilization=sys_info.cpu_percent,
                memory_utilization=sys_info.memory_percent,
                temperature_celsius=sys_info.temperature_c,
                uptime_seconds=sys_info.uptime_seconds,
                is_reachable=ping_res.is_reachable,
                latency_ms=ping_res.avg_rtt_ms,
                packet_loss_pct=ping_res.packet_loss_percent,
            )
            db.add(dev_metric)

            # Update live device stats
            device.cpu_utilization = sys_info.cpu_percent
            device.memory_utilization = sys_info.memory_percent
            device.temperature_celsius = sys_info.temperature_c
            device.uptime_seconds = sys_info.uptime_seconds
            device.last_seen = datetime.now(timezone.utc)
            if ping_res.packet_loss_percent > 20.0 or sys_info.cpu_percent > 90.0:
                device.status = DeviceStatus.WARNING
            elif not ping_res.is_reachable:
                device.status = DeviceStatus.CRITICAL
            else:
                device.status = DeviceStatus.ONLINE

            # 2. Interface metrics
            iface_infos = await adapter.get_interfaces()
            for if_info in iface_infos:
                db_if = next((i for i in device.interfaces if i.name == if_info.name), None)
                if db_if:
                    db_if.rx_bps = if_info.rx_bps
                    db_if.tx_bps = if_info.tx_bps
                    db_if.rx_pps = if_info.rx_pps
                    db_if.tx_pps = if_info.tx_pps
                    db_if.rx_errors += if_info.rx_errors
                    db_if.tx_errors += if_info.tx_errors
                    db_if.rx_drops += if_info.rx_drops

                    speed_bps = max(1_000_000, db_if.speed_mbps * 1_000_000)
                    util_pct = min(100.0, (max(if_info.rx_bps, if_info.tx_bps) / speed_bps) * 100.0)

                    if_metric = InterfaceMetric(
                        interface_id=db_if.id,
                        rx_bps=if_info.rx_bps,
                        tx_bps=if_info.tx_bps,
                        rx_pps=if_info.rx_pps,
                        tx_pps=if_info.tx_pps,
                        rx_errors=if_info.rx_errors,
                        tx_errors=if_info.tx_errors,
                        rx_drops=if_info.rx_drops,
                        tx_drops=if_info.tx_drops,
                        utilization_pct=round(util_pct, 2),
                    )
                    db.add(if_metric)

            await db.commit()

            # Broadcast live telemetry over WebSocket
            await ws_manager.broadcast_telemetry(
                device_id=device.id,
                metrics={
                    "hostname": device.hostname,
                    "cpu": sys_info.cpu_percent,
                    "memory": sys_info.memory_percent,
                    "temperature": sys_info.temperature_c,
                    "latency": ping_res.avg_rtt_ms,
                    "packet_loss": ping_res.packet_loss_percent,
                    "status": device.status.value,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        except Exception as e:
            device.status = DeviceStatus.CRITICAL
            await db.commit()

    @staticmethod
    async def run_poll_cycle():
        """Poll all active devices in inventory with isolated sessions and bounded concurrency."""
        async with AsyncSessionLocal() as session:
            stmt = select(Device.id).where(Device.is_managed == True)
            res = await session.execute(stmt)
            device_ids = res.scalars().all()

        semaphore = asyncio.Semaphore(10)

        async def worker(dev_id: int):
            async with semaphore:
                async with AsyncSessionLocal() as worker_session:
                    dev_stmt = select(Device).options(selectinload(Device.interfaces)).where(Device.id == dev_id)
                    dev_res = await worker_session.execute(dev_stmt)
                    dev = dev_res.scalar_one_or_none()
                    if dev:
                        await TelemetryCollector.collect_single_device(worker_session, dev)

        tasks = [worker(did) for did in device_ids]
        await asyncio.gather(*tasks, return_exceptions=True)
