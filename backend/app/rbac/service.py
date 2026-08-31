"""
Service layer for role management, permission checking, and database seeding.
"""

from typing import List, Set, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from backend.app.rbac.models import Role, PermissionModel, RolePermission, UserRole
from backend.app.rbac.permissions import Permission, RoleName, ROLE_PERMISSIONS
from backend.app.rbac.schemas import RoleCreate, RoleUpdate


class RBACService:
    @staticmethod
    async def initialize_roles_and_permissions(db: AsyncSession):
        """Seed all default permissions and system roles into database if not present."""
        # 1. Insert permissions
        result = await db.execute(select(PermissionModel))
        existing_perms = {p.code: p for p in result.scalars().all()}

        for perm in Permission:
            if perm.value not in existing_perms:
                category = perm.value.split(".")[0]
                desc = f"Permission for {perm.value.replace('.', ' ').title()}"
                p_model = PermissionModel(code=perm.value, category=category, description=desc)
                db.add(p_model)
                existing_perms[perm.value] = p_model

        await db.flush()

        # 2. Insert or update system roles
        result = await db.execute(select(Role).options(selectinload(Role.role_permissions)))
        existing_roles = {r.name: r for r in result.scalars().all()}

        for role_name, perms in ROLE_PERMISSIONS.items():
            if role_name.value not in existing_roles:
                role = Role(
                    name=role_name.value,
                    description=f"System {role_name.value.replace('_', ' ').title()} Role",
                    is_system_role=True
                )
                db.add(role)
                await db.flush()
                existing_roles[role_name.value] = role
            else:
                role = existing_roles[role_name.value]

            # Clear and assign permissions
            await db.execute(delete(RolePermission).where(RolePermission.role_id == role.id))
            for perm in perms:
                p_obj = existing_perms.get(perm.value)
                if p_obj:
                    rp = RolePermission(role_id=role.id, permission_id=p_obj.id)
                    db.add(rp)

        await db.commit()

    @staticmethod
    async def get_user_permissions(db: AsyncSession, user_id: int) -> Set[str]:
        """Fetch unified set of all permission strings for given user."""
        query = (
            select(PermissionModel.code)
            .join(RolePermission, RolePermission.permission_id == PermissionModel.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        result = await db.execute(query)
        return set(result.scalars().all())

    @staticmethod
    async def get_user_roles(db: AsyncSession, user_id: int) -> List[str]:
        """Fetch list of role names assigned to user."""
        query = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def list_roles(db: AsyncSession) -> List[Role]:
        """List all system and custom roles with permissions."""
        result = await db.execute(select(Role).options(selectinload(Role.role_permissions).selectinload(RolePermission.permission)))
        return list(result.scalars().all())

    @staticmethod
    async def create_role(db: AsyncSession, data: RoleCreate) -> Role:
        """Create new custom role with assigned permissions."""
        role = Role(name=data.name, description=data.description, is_system_role=False)
        db.add(role)
        await db.flush()

        for code in data.permissions:
            res = await db.execute(select(PermissionModel).where(PermissionModel.code == code))
            p_obj = res.scalar_one_or_none()
            if p_obj:
                db.add(RolePermission(role_id=role.id, permission_id=p_obj.id))

        await db.commit()
        return role

    @staticmethod
    async def assign_user_roles(db: AsyncSession, user_id: int, role_names: List[str]):
        """Assign list of roles to user."""
        await db.execute(delete(UserRole).where(UserRole.user_id == user_id))
        for rname in role_names:
            res = await db.execute(select(Role).where(Role.name == rname))
            role = res.scalar_one_or_none()
            if role:
                db.add(UserRole(user_id=user_id, role_id=role.id))
        await db.commit()
