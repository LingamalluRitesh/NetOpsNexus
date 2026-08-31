"""
Pydantic schemas for RBAC roles, permissions, and assignment workflows.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PermissionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    category: str
    description: str


class RoleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=64)
    description: str = Field(..., max_length=255)


class RoleCreate(RoleBase):
    permissions: List[str]


class RoleUpdate(BaseModel):
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_system_role: bool
    permissions: List[str]


class UserRoleAssignment(BaseModel):
    user_id: int
    roles: List[str]
