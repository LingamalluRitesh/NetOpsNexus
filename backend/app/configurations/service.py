"""
Service layer for Configuration backups, template management, staged deployments, and manual rollbacks.
"""

from typing import List, Optional, Tuple, Dict, Any
import hashlib
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.devices.models import Device
from backend.app.configurations.models import (
    DeviceConfig, ConfigTemplate, ConfigDeployment, DeploymentLog, BackupType, DeploymentStatus
)
from backend.app.configurations.schemas import (
    ConfigVersionResponse, ConfigTemplateCreate, ConfigTemplateResponse,
    ConfigDeploymentCreate, ConfigDeploymentResponse, RollbackRequest, ConfigDiffResponse
)
from backend.app.configurations.diff_engine import ConfigDiffEngine
from backend.app.configurations.deployment_engine import DeploymentEngine
from backend.app.adapters.manager import AdapterManager


class ConfigService:
    @staticmethod
    async def get_device_backup_history(db: AsyncSession, device_id: int) -> List[DeviceConfig]:
        """Fetch all configuration backup versions for device."""
        stmt = (
            select(DeviceConfig)
            .where(DeviceConfig.device_id == device_id)
            .order_by(DeviceConfig.version_number.desc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_device_backup(
        db: AsyncSession,
        device_id: int,
        backup_type: BackupType = BackupType.MANUAL,
        comment: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> DeviceConfig:
        """Pull live running configuration from device and record a new version."""
        res_dev = await db.execute(select(Device).where(Device.id == device_id))
        device = res_dev.scalar_one_or_none()
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

        adapter = AdapterManager.get_adapter(device.management_ip)
        config_text = await adapter.get_running_config()
        cfg_hash = hashlib.sha256(config_text.encode("utf-8")).hexdigest()

        # Find latest version
        latest_res = await db.execute(
            select(DeviceConfig).where(DeviceConfig.device_id == device_id).order_by(DeviceConfig.version_number.desc())
        )
        latest = latest_res.scalars().first()
        next_version = (latest.version_number + 1) if latest else 1

        backup = DeviceConfig(
            device_id=device_id,
            version_number=next_version,
            config_text=config_text,
            config_hash=cfg_hash,
            backup_type=backup_type,
            created_by_id=user_id,
            comment=comment or f"Manual backup v{next_version}",
        )
        db.add(backup)
        await db.commit()
        await db.refresh(backup)
        return backup

    @staticmethod
    async def rollback_device(db: AsyncSession, req: RollbackRequest, user_id: Optional[int] = None) -> DeviceConfig:
        """Atomic rollback: Revert device running-config to a specific past version."""
        res_target = await db.execute(select(DeviceConfig).where(DeviceConfig.id == req.target_version_id))
        target_cfg = res_target.scalar_one_or_none()
        if not target_cfg or target_cfg.device_id != req.device_id:
            raise HTTPException(status_code=404, detail="Target configuration version not found")

        res_dev = await db.execute(select(Device).where(Device.id == req.device_id))
        device = res_dev.scalar_one_or_none()
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        adapter = AdapterManager.get_adapter(device.management_ip)
        apply_res = await adapter.apply_config(target_cfg.config_text)
        if apply_res.status != "success":
            raise HTTPException(status_code=500, detail=f"Failed to apply rollback configuration: {apply_res.output}")

        # Record new restore version
        return await ConfigService.create_device_backup(
            db,
            device_id=req.device_id,
            backup_type=BackupType.ROLLBACK_RESTORE,
            comment=f"Rollback restored from v{target_cfg.version_number}: {req.comment}",
            user_id=user_id,
        )

    @staticmethod
    async def list_templates(db: AsyncSession) -> List[ConfigTemplate]:
        stmt = select(ConfigTemplate).where(ConfigTemplate.is_active == True).order_by(ConfigTemplate.name)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    async def create_template(db: AsyncSession, data: ConfigTemplateCreate, user_id: Optional[int] = None) -> ConfigTemplate:
        template = ConfigTemplate(**data.model_dump(), created_by_id=user_id)
        db.add(template)
        await db.commit()
        await db.refresh(template)
        return template

    @staticmethod
    async def create_deployment(db: AsyncSession, data: ConfigDeploymentCreate, user_id: Optional[int] = None) -> ConfigDeployment:
        deployment = ConfigDeployment(
            title=data.title,
            description=data.description,
            status=DeploymentStatus.PENDING_APPROVAL if data.approval_required else DeploymentStatus.APPROVED,
            target_device_ids=data.target_device_ids,
            template_id=data.template_id,
            template_vars=data.template_vars or {},
            raw_config_text=data.raw_config_text,
            approval_required=data.approval_required,
            created_by_id=user_id,
        )
        db.add(deployment)
        await db.commit()
        await db.refresh(deployment)

        # If no approval required, execute immediately
        if not data.approval_required:
            await DeploymentEngine.execute_deployment(db, deployment)

        return deployment

    @staticmethod
    async def approve_and_deploy(db: AsyncSession, deployment_id: int, user_id: Optional[int] = None) -> ConfigDeployment:
        stmt = select(ConfigDeployment).where(ConfigDeployment.id == deployment_id)
        res = await db.execute(stmt)
        deployment = res.scalar_one_or_none()
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        deployment.status = DeploymentStatus.APPROVED
        deployment.approved_by_id = user_id
        await db.commit()

        return await DeploymentEngine.execute_deployment(db, deployment)
