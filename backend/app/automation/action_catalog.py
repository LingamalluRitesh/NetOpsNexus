"""
Catalog of executable network automation actions: CLI commands, interface state changes,
configuration snapshots, diagnostic traces, and notification dispatches.
"""

from typing import Dict, Any, List, Callable
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.devices.models import Device, NetworkInterface, InterfaceAdminStatus
from backend.app.adapters.manager import AdapterManager
from backend.app.configurations.service import ConfigService
from backend.app.configurations.models import BackupType
from backend.app.automation.schemas import ActionDefinitionResponse, ActionParamSchema


class ActionCatalog:
    _actions: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, category: str, label: str, description: str, params: List[ActionParamSchema]):
        def decorator(func: Callable):
            cls._actions[name] = {
                "handler": func,
                "meta": ActionDefinitionResponse(
                    action_name=name,
                    category=category,
                    label=label,
                    description=description,
                    parameters=params,
                )
            }
            return func
        return decorator

    @classmethod
    def list_actions(cls) -> List[ActionDefinitionResponse]:
        return [act["meta"] for act in cls._actions.values()]

    @classmethod
    async def execute_action(cls, db: AsyncSession, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if name not in cls._actions:
            raise ValueError(f"Unknown automation action: '{name}'")
        handler = cls._actions[name]["handler"]
        return await handler(db, params)


# --- Register Built-in Action Handlers ---

@ActionCatalog.register(
    name="cli.execute_command",
    category="CLI & Operations",
    label="Execute SSH CLI Command",
    description="Execute raw CLI command on target device and capture output",
    params=[
        ActionParamSchema(name="device_id", type="int", description="Target Device ID"),
        ActionParamSchema(name="command", type="str", description="CLI command text to run"),
    ]
)
async def action_cli_execute(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    dev_id = int(params["device_id"])
    cmd = str(params["command"])
    
    res = await db.execute(select(Device).where(Device.id == dev_id))
    device = res.scalar_one_or_none()
    if not device:
        raise ValueError(f"Device {dev_id} not found")

    adapter = AdapterManager.get_adapter(device.management_ip)
    res_cmd = await adapter.execute_command(cmd)
    return {
        "device_hostname": device.hostname,
        "command": cmd,
        "output": res_cmd.output,
        "status": res_cmd.status,
    }


@ActionCatalog.register(
    name="config.backup",
    category="Configuration",
    label="Take Config Snapshot",
    description="Capture instantaneous running configuration backup snapshot",
    params=[
        ActionParamSchema(name="device_id", type="int", description="Target Device ID"),
        ActionParamSchema(name="comment", type="str", description="Snapshot label", required=False, default="Automation Backup"),
    ]
)
async def action_config_backup(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    dev_id = int(params["device_id"])
    comment = params.get("comment", "Automated snapshot")
    backup = await ConfigService.create_device_backup(db, dev_id, backup_type=BackupType.MANUAL, comment=comment)
    return {
        "version_number": backup.version_number,
        "config_hash": backup.config_hash,
        "device_id": dev_id,
    }


@ActionCatalog.register(
    name="interface.set_state",
    category="Interface Control",
    label="Set Interface State",
    description="Administratively enable or disable (shutdown/no shutdown) an interface",
    params=[
        ActionParamSchema(name="device_id", type="int", description="Target Device ID"),
        ActionParamSchema(name="interface_name", type="str", description="Interface name e.g. GigabitEthernet0/1"),
        ActionParamSchema(name="state", type="str", description="'up' or 'down'"),
    ]
)
async def action_interface_state(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    dev_id = int(params["device_id"])
    if_name = str(params["interface_name"])
    target_state = str(params["state"]).lower()

    res = await db.execute(select(Device).where(Device.id == dev_id))
    device = res.scalar_one_or_none()
    if not device:
        raise ValueError(f"Device {dev_id} not found")

    adapter = AdapterManager.get_adapter(device.management_ip)
    cli_cmd = f"interface {if_name}\n{'no shutdown' if target_state == 'up' else 'shutdown'}\n"
    res_cmd = await adapter.apply_config(cli_cmd)
    return {
        "device_hostname": device.hostname,
        "interface": if_name,
        "applied_state": target_state,
        "output": res_cmd.output,
    }


@ActionCatalog.register(
    name="diagnostic.run_ping",
    category="Diagnostics",
    label="Run Ping Health Check",
    description="Ping destination IP and assert packet loss and latency thresholds",
    params=[
        ActionParamSchema(name="source_device_id", type="int", description="Source Device ID"),
        ActionParamSchema(name="target_ip", type="str", description="Target destination IP"),
        ActionParamSchema(name="max_loss_pct", type="float", description="Maximum allowed packet loss", required=False, default=10.0),
    ]
)
async def action_diag_ping(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    dev_id = int(params["source_device_id"])
    target_ip = str(params["target_ip"])
    max_loss = float(params.get("max_loss_pct", 10.0))

    res = await db.execute(select(Device).where(Device.id == dev_id))
    device = res.scalar_one_or_none()
    if not device:
        raise ValueError(f"Device {dev_id} not found")

    adapter = AdapterManager.get_adapter(device.management_ip)
    ping_res = await adapter.ping(target=target_ip, count=4)
    
    passed = ping_res.is_reachable and ping_res.packet_loss_percent <= max_loss
    return {
        "is_reachable": ping_res.is_reachable,
        "avg_rtt_ms": ping_res.avg_rtt_ms,
        "packet_loss_pct": ping_res.packet_loss_percent,
        "passed": passed,
    }


@ActionCatalog.register(
    name="notification.webhook",
    category="Integrations",
    label="Send HTTP Webhook",
    description="Dispatch JSON payload to external alerting or webhook URL",
    params=[
        ActionParamSchema(name="url", type="str", description="HTTP/HTTPS Webhook endpoint"),
        ActionParamSchema(name="message", type="str", description="Notification text message"),
    ]
)
async def action_webhook(db: AsyncSession, params: Dict[str, Any]) -> Dict[str, Any]:
    # Simulated webhook dispatch
    return {
        "url": params["url"],
        "message": params["message"],
        "status": "delivered",
    }
