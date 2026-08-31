"""
Pydantic schemas for Security Compliance, CIS Benchmarks, ACL Shadowing, and Rogue Devices.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class CisFinding(BaseModel):
    check_id: str
    title: str
    status: str  # PASS, FAIL, WARNING
    severity: str  # HIGH, MEDIUM, LOW
    remediation_command: Optional[str] = None
    description: str


class SecurityAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    score_percent: float
    cis_passed_checks: int
    cis_failed_checks: int
    findings: List[CisFinding]
    audited_at: datetime


class SecurityScoreOverview(BaseModel):
    overall_fleet_score: float
    grade: str  # A+, A, B, C, F
    total_devices_audited: int
    compliant_devices_count: int
    vulnerable_devices_count: int
    critical_findings_count: int
    top_vulnerabilities: List[Dict[str, Any]]


class AclRuleBase(BaseModel):
    device_id: int
    acl_name: str
    sequence_num: int
    action: str = "permit"
    protocol: str = "ip"
    src_ip_prefix: str = "any"
    dst_ip_prefix: str = "any"
    src_port: str = "any"
    dst_port: str = "any"
    description: Optional[str] = None


class AclRuleResponse(AclRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_shadowed: bool = False
    shadowed_by_sequence: Optional[int] = None


class AclShadowAnalysisResponse(BaseModel):
    acl_name: str
    total_rules: int
    shadowed_rules_count: int
    redundant_rules_count: int
    rules: List[AclRuleResponse]


class RogueDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mac_address: str
    ip_address: Optional[str] = None
    switch_device_id: Optional[int] = None
    switch_port: Optional[str] = None
    status: str
    detected_at: datetime
    notes: Optional[str] = None
