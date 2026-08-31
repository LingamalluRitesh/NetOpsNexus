"""
RBAC API endpoints for role inspection, role creation, permission listing, and user role management.
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.database import get_db
from backend.app.dependencies import require_permission, get_current_user
from backend.app.rbac.permissions import Permission
from backend.app.rbac.models import Role, PermissionModel, RolePermission, UserRole
from backend.app.rbac.schemas import RoleResponse, RoleCreate, PermissionSchema, UserRoleAssignment
from backend.app.rbac.service import RBACService
from backend.app.auth.models import User
from backend.app.auth.schemas import UserResponse, UserCreate
from backend.app.auth.service import AuthService

router = APIRouter(prefix="/rbac", tags=["Role-Based Access Control"])


@router.get("/permissions", response_model=List[PermissionSchema])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.RBAC_READ))
) -> Any:
    """List all available system permissions."""
    result = await db.execute(select(PermissionModel).order_by(PermissionModel.category, PermissionModel.code))
    return result.scalars().all()


@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.RBAC_READ))
) -> Any:
    """List all roles and their associated permissions."""
    roles = await RBACService.list_roles(db)
    response = []
    for r in roles:
        perms = [rp.permission.code for rp in r.role_permissions if rp.permission]
        response.append(
            RoleResponse(
                id=r.id,
                name=r.name,
                description=r.description,
                is_system_role=r.is_system_role,
                permissions=perms,
            )
        )
    return response


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.RBAC_WRITE))
) -> Any:
    """Create a new custom role with specified permissions."""
    existing = await db.execute(select(Role).where(Role.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Role '{data.name}' already exists")

    role = await RBACService.create_role(db, data)
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        is_system_role=role.is_system_role,
        permissions=data.permissions,
    )


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.RBAC_READ))
) -> Any:
    """List all users with their assigned roles and permissions."""
    result = await db.execute(select(User).order_by(User.id))
    users = result.scalars().all()
    user_responses = []
    for u in users:
        roles = await RBACService.get_user_roles(db, u.id)
        perms = await RBACService.get_user_permissions(db, u.id)
        user_responses.append(
            UserResponse(
                id=u.id,
                username=u.username,
                email=u.email,
                full_name=u.full_name,
                is_active=u.is_active,
                is_superuser=u.is_superuser,
                roles=roles,
                permissions=list(perms),
                last_login=u.last_login,
                created_at=u.created_at,
            )
        )
    return user_responses


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.RBAC_WRITE))
) -> Any:
    """Create a new user and assign roles."""
    user = await AuthService.create_user(db, data)
    roles = await RBACService.get_user_roles(db, user.id)
    perms = await RBACService.get_user_permissions(db, user.id)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        roles=roles,
        permissions=list(perms),
        last_login=user.last_login,
        created_at=user.created_at,
    )


@router.put("/users/{user_id}/roles")
async def update_user_roles(
    user_id: int,
    data: UserRoleAssignment,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_permission(Permission.RBAC_WRITE))
) -> Any:
    """Update role assignments for a user."""
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await RBACService.assign_user_roles(db, user_id, data.roles)
    return {"message": f"Successfully updated roles for user {user.username}"}
