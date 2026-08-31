"""
Device inventory, interfaces, routing tables, and sites domain module.
"""

from backend.app.devices.models import (
    Device, Site, Rack, NetworkInterface, RoutingTableEntry, Vlan,
    DeviceType, DeviceStatus, InterfaceOperStatus, InterfaceAdminStatus, RouteProtocol
)
from backend.app.devices.repository import DeviceRepository, SiteRepository
from backend.app.devices.service import DeviceService
from backend.app.devices.router import router as device_router, site_router

__all__ = [
    "Device", "Site", "Rack", "NetworkInterface", "RoutingTableEntry", "Vlan",
    "DeviceType", "DeviceStatus", "InterfaceOperStatus", "InterfaceAdminStatus", "RouteProtocol",
    "DeviceRepository", "SiteRepository", "DeviceService", "device_router", "site_router"
]
