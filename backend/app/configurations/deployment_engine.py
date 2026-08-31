"""
Deployment Engine: Staged rollout orchestrator with pre-checks, automatic snapshots,
health verification gates, and atomic rollback on verification failure.
"""

from typing import List, Dict, Any
import hashlib
import time
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.devices.models import Device, DeviceStatus
from backend.app.configurations.models import (
    ConfigDeployment, DeploymentLog, DeviceConfig, BackupType, DeploymentStatus
)
from backend.app.configurations.diff_engine import ConfigDiffEngine
from backend.app.adapters.manager import AdapterManager
from backend.app.websocket_manager import ws_manager


class DeploymentEngine:
    @staticmethod
    async def execute_deployment(db: AsyncSession, deployment: ConfigDeployment) -> ConfigDeployment:
        """Execute multi-device staged configuration deployment with automated rollback."""
        deployment.status = DeploymentStatus.DEPLOYING
        deployment.started_at = datetime.now(timezone.utc)
        await db.commit()

        target_devices_res = await db.execute(
            select(Device).where(Device.id.in_(deployment.target_device_ids))
        )
        devices = target_devices_res.scalars().all()

        config_to_push = deployment.raw_config_text or ""
        if deployment.template:
            from backend.app.configurations.template_engine import ConfigTemplateEngine
            t_engine = ConfigTemplateEngine()
            render_res = t_engine.render_template(deployment.template.template_text, deployment.template_vars or {})
            if not render_res.syntax_valid:
                deployment.status = DeploymentStatus.FAILED
                deployment.completed_at = datetime.now(timezone.utc)
                await db.commit()
                return deployment
            config_to_push = render_res.rendered_config

        overall_success = True

        for device in devices:
            adapter = AdapterManager.get_adapter(device.management_ip)
            
            # Step 1: Pre-check & Reachability
            ping_res = await adapter.ping(count=2, timeout_sec=1.0)
            if not ping_res.is_reachable:
                log_entry = DeploymentLog(
                    deployment_id=deployment.id,
                    device_id=device.id,
                    step_name="pre_check",
                    status="failed",
                    log_output=f"Device {device.hostname} unreachable prior to deployment",
                )
                db.add(log_entry)
                overall_success = False
                continue

            # Step 2: Automatic Pre-Deployment Configuration Backup Snapshot
            running_before = await adapter.get_running_config()
            cfg_hash = hashlib.sha256(running_before.encode("utf-8")).hexdigest()

            # Find latest version number
            latest_cfg_res = await db.execute(
                select(DeviceConfig).where(DeviceConfig.device_id == device.id).order_by(DeviceConfig.version_number.desc())
            )
            latest_cfg = latest_cfg_res.scalars().first()
            next_ver = (latest_cfg.version_number + 1) if latest_cfg else 1

            pre_backup = DeviceConfig(
                device_id=device.id,
                version_number=next_ver,
                config_text=running_before,
                config_hash=cfg_hash,
                backup_type=BackupType.PRE_DEPLOYMENT,
                created_by_id=deployment.created_by_id,
                comment=f"Auto snapshot prior to deployment #{deployment.id}",
            )
            db.add(pre_backup)
            await db.flush()

            # Step 3: Compute Diff
            diff_res = ConfigDiffEngine.compare_configs(running_before, config_to_push)

            # Step 4: Apply Configuration
            cmd_res = await adapter.apply_config(config_to_push)
            
            if cmd_res.status != "success":
                # Push failed
                db.add(
                    DeploymentLog(
                        deployment_id=deployment.id,
                        device_id=device.id,
                        step_name="apply",
                        status="failed",
                        log_output=f"Apply failed: {cmd_res.output}",
                        diff_text=diff_res.unified_diff,
                        rollback_version_id=pre_backup.id,
                    )
                )
                overall_success = False
                continue

            # Step 5: Post-Deployment Verification Gate
            time.sleep(0.1)
            post_ping = await adapter.ping(count=2, timeout_sec=1.0)
            
            if not post_ping.is_reachable or post_ping.packet_loss_percent > 50.0:
                # Verification Failed -> Trigger Automated Rollback
                rollback_res = await adapter.apply_config(running_before)
                db.add(
                    DeploymentLog(
                        deployment_id=deployment.id,
                        device_id=device.id,
                        step_name="rollback",
                        status="warning",
                        log_output=f"Verification failed (loss {post_ping.packet_loss_percent}%). Auto rollback executed: {rollback_res.output}",
                        diff_text=diff_res.unified_diff,
                        rollback_version_id=pre_backup.id,
                    )
                )
                overall_success = False
            else:
                # Verified successfully
                # Save Post-deployment version
                running_after = await adapter.get_running_config()
                post_hash = hashlib.sha256(running_after.encode("utf-8")).hexdigest()
                post_backup = DeviceConfig(
                    device_id=device.id,
                    version_number=next_ver + 1,
                    config_text=running_after,
                    config_hash=post_hash,
                    backup_type=BackupType.POST_DEPLOYMENT,
                    created_by_id=deployment.created_by_id,
                    comment=f"Auto snapshot after deployment #{deployment.id}",
                )
                db.add(post_backup)

                db.add(
                    DeploymentLog(
                        deployment_id=deployment.id,
                        device_id=device.id,
                        step_name="verify",
                        status="success",
                        log_output=f"Deployment verified successfully. Changes: +{diff_res.additions} -{diff_res.deletions}",
                        diff_text=diff_res.unified_diff,
                        rollback_version_id=pre_backup.id,
                    )
                )

        deployment.status = DeploymentStatus.VERIFIED if overall_success else DeploymentStatus.FAILED
        deployment.completed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(deployment)
        return deployment
