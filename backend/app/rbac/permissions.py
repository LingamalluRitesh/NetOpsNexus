"""
Enterprise RBAC permission matrix and standard role definitions.
"""

from enum import Enum
from typing import Dict, List, Set


class Permission(str, Enum):
    # Device Inventory
    DEVICES_READ = "devices.read"
    DEVICES_WRITE = "devices.write"
    DEVICES_DELETE = "devices.delete"
    
    # Discovery
    DISCOVERY_RUN = "discovery.run"
    DISCOVERY_READ = "discovery.read"
    
    # Topology
    TOPOLOGY_READ = "topology.read"
    TOPOLOGY_WRITE = "topology.write"
    
    # Monitoring & Telemetry
    MONITORING_READ = "monitoring.read"
    MONITORING_WRITE = "monitoring.write"
    
    # IPAM
    IPAM_READ = "ipam.read"
    IPAM_WRITE = "ipam.write"
    
    # Configuration Management (NCM)
    CONFIGS_READ = "configs.read"
    CONFIGS_WRITE = "configs.write"
    CONFIGS_DEPLOY = "configs.deploy"
    CONFIGS_ROLLBACK = "configs.rollback"
    
    # Workflow Automation
    AUTOMATION_READ = "automation.read"
    AUTOMATION_WRITE = "automation.write"
    AUTOMATION_EXECUTE = "automation.execute"
    
    # Incidents & Alerts
    INCIDENTS_READ = "incidents.read"
    INCIDENTS_CREATE = "incidents.create"
    INCIDENTS_ASSIGN = "incidents.assign"
    INCIDENTS_WRITE = "incidents.write"
    ALERTS_READ = "alerts.read"
    ALERTS_ACK = "alerts.ack"
    ALERTS_WRITE = "alerts.write"
    
    # Security
    SECURITY_READ = "security.read"
    SECURITY_WRITE = "security.write"
    
    # Traffic Intelligence
    TRAFFIC_READ = "traffic.read"
    TRAFFIC_WRITE = "traffic.write"
    
    # Diagnostics & Health
    DIAGNOSTICS_RUN = "diagnostics.run"
    HEALTH_READ = "health.read"
    CAPACITY_READ = "capacity.read"
    
    # Reporting & Audit
    REPORTS_EXPORT = "reports.export"
    AUDIT_READ = "audit.read"
    
    # Administration & RBAC
    RBAC_READ = "rbac.read"
    RBAC_WRITE = "rbac.write"
    SYSTEM_ADMIN = "system.admin"


class RoleName(str, Enum):
    SUPER_ADMIN = "super_admin"
    NETWORK_ADMIN = "network_admin"
    NETWORK_ENGINEER = "network_engineer"
    SECURITY_ENGINEER = "security_engineer"
    NOC_ENGINEER = "noc_engineer"
    AUDITOR = "auditor"
    READ_ONLY = "read_only"


# Mapping of system roles to their granted permissions
ROLE_PERMISSIONS: Dict[RoleName, List[Permission]] = {
    RoleName.SUPER_ADMIN: [perm for perm in Permission],
    
    RoleName.NETWORK_ADMIN: [
        Permission.DEVICES_READ, Permission.DEVICES_WRITE, Permission.DEVICES_DELETE,
        Permission.DISCOVERY_RUN, Permission.DISCOVERY_READ,
        Permission.TOPOLOGY_READ, Permission.TOPOLOGY_WRITE,
        Permission.MONITORING_READ, Permission.MONITORING_WRITE,
        Permission.IPAM_READ, Permission.IPAM_WRITE,
        Permission.CONFIGS_READ, Permission.CONFIGS_WRITE, Permission.CONFIGS_DEPLOY, Permission.CONFIGS_ROLLBACK,
        Permission.AUTOMATION_READ, Permission.AUTOMATION_WRITE, Permission.AUTOMATION_EXECUTE,
        Permission.INCIDENTS_READ, Permission.INCIDENTS_CREATE, Permission.INCIDENTS_ASSIGN, Permission.INCIDENTS_WRITE,
        Permission.ALERTS_READ, Permission.ALERTS_ACK, Permission.ALERTS_WRITE,
        Permission.SECURITY_READ,
        Permission.TRAFFIC_READ, Permission.TRAFFIC_WRITE,
        Permission.DIAGNOSTICS_RUN, Permission.HEALTH_READ, Permission.CAPACITY_READ,
        Permission.REPORTS_EXPORT, Permission.AUDIT_READ,
        Permission.RBAC_READ,
    ],
    
    RoleName.NETWORK_ENGINEER: [
        Permission.DEVICES_READ, Permission.DEVICES_WRITE,
        Permission.DISCOVERY_RUN, Permission.DISCOVERY_READ,
        Permission.TOPOLOGY_READ,
        Permission.MONITORING_READ,
        Permission.IPAM_READ,
        Permission.CONFIGS_READ, Permission.CONFIGS_WRITE, Permission.CONFIGS_DEPLOY, Permission.CONFIGS_ROLLBACK,
        Permission.AUTOMATION_READ, Permission.AUTOMATION_EXECUTE,
        Permission.INCIDENTS_READ, Permission.INCIDENTS_CREATE, Permission.INCIDENTS_WRITE,
        Permission.ALERTS_READ, Permission.ALERTS_ACK,
        Permission.SECURITY_READ,
        Permission.TRAFFIC_READ,
        Permission.DIAGNOSTICS_RUN, Permission.HEALTH_READ, Permission.CAPACITY_READ,
        Permission.REPORTS_EXPORT,
    ],
    
    RoleName.SECURITY_ENGINEER: [
        Permission.DEVICES_READ,
        Permission.TOPOLOGY_READ,
        Permission.MONITORING_READ,
        Permission.IPAM_READ,
        Permission.CONFIGS_READ,
        Permission.INCIDENTS_READ, Permission.INCIDENTS_CREATE, Permission.INCIDENTS_WRITE,
        Permission.ALERTS_READ, Permission.ALERTS_ACK,
        Permission.SECURITY_READ, Permission.SECURITY_WRITE,
        Permission.TRAFFIC_READ,
        Permission.DIAGNOSTICS_RUN, Permission.HEALTH_READ,
        Permission.REPORTS_EXPORT, Permission.AUDIT_READ,
    ],
    
    RoleName.NOC_ENGINEER: [
        Permission.DEVICES_READ,
        Permission.DISCOVERY_READ,
        Permission.TOPOLOGY_READ,
        Permission.MONITORING_READ,
        Permission.IPAM_READ,
        Permission.INCIDENTS_READ, Permission.INCIDENTS_CREATE, Permission.INCIDENTS_ASSIGN, Permission.INCIDENTS_WRITE,
        Permission.ALERTS_READ, Permission.ALERTS_ACK,
        Permission.SECURITY_READ,
        Permission.TRAFFIC_READ,
        Permission.DIAGNOSTICS_RUN, Permission.HEALTH_READ, Permission.CAPACITY_READ,
        Permission.REPORTS_EXPORT,
    ],
    
    RoleName.AUDITOR: [
        Permission.DEVICES_READ,
        Permission.TOPOLOGY_READ,
        Permission.MONITORING_READ,
        Permission.IPAM_READ,
        Permission.CONFIGS_READ,
        Permission.AUTOMATION_READ,
        Permission.INCIDENTS_READ,
        Permission.ALERTS_READ,
        Permission.SECURITY_READ,
        Permission.TRAFFIC_READ,
        Permission.HEALTH_READ,
        Permission.CAPACITY_READ,
        Permission.REPORTS_EXPORT,
        Permission.AUDIT_READ,
        Permission.RBAC_READ,
    ],
    
    RoleName.READ_ONLY: [
        Permission.DEVICES_READ,
        Permission.TOPOLOGY_READ,
        Permission.MONITORING_READ,
        Permission.IPAM_READ,
        Permission.CONFIGS_READ,
        Permission.AUTOMATION_READ,
        Permission.INCIDENTS_READ,
        Permission.ALERTS_READ,
        Permission.HEALTH_READ,
        Permission.CAPACITY_READ,
    ],
}
