"""
SQLAlchemy models for enterprise RBAC roles, permissions, and mappings.
"""

from typing import List
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database import Base


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    is_system_role: Mapped[bool] = mapped_column(default=True)

    # Relationships
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan", lazy="selectin"
    )
    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan", lazy="selectin"
    )


class PermissionModel(Base):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission", back_populates="permission", cascade="all, delete-orphan"
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True)

    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["PermissionModel"] = relationship("PermissionModel", back_populates="role_permissions", lazy="selectin")


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)

    user: Mapped["backend.app.auth.models.User"] = relationship("backend.app.auth.models.User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles", lazy="selectin")
