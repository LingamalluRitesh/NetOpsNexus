"""
CIS Benchmark Security Audit Engine inspecting running configurations against CIS hardening standards.
"""

from typing import List, Dict, Any, Tuple
from backend.app.security.schemas import CisFinding


class CisBenchmarkAuditor:
    @staticmethod
    def audit_cisco_config(config_text: str) -> Tuple[float, List[CisFinding]]:
        """Audit Cisco IOS / XE configuration against CIS Network Device Benchmarks."""
        findings: List[CisFinding] = []
        passed = 0
        total = 0

        # Check 1: AAA Authentication
        total += 1
        if "aaa new-model" in config_text:
            passed += 1
            findings.append(CisFinding(
                check_id="CIS-1.1",
                title="AAA Authentication Model",
                status="PASS",
                severity="HIGH",
                description="AAA new-model is enabled on the device.",
            ))
        else:
            findings.append(CisFinding(
                check_id="CIS-1.1",
                title="AAA Authentication Model",
                status="FAIL",
                severity="HIGH",
                remediation_command="aaa new-model",
                description="AAA model is disabled; legacy authentication in use.",
            ))

        # Check 2: Telnet disabled / SSH only
        total += 1
        if "transport input ssh" in config_text or ("transport input" in config_text and "telnet" not in config_text):
            passed += 1
            findings.append(CisFinding(
                check_id="CIS-2.1",
                title="Secure Management Transport (SSH)",
                status="PASS",
                severity="HIGH",
                description="VTY lines configured for SSH only; Telnet is disabled.",
            ))
        else:
            findings.append(CisFinding(
                check_id="CIS-2.1",
                title="Secure Management Transport (SSH)",
                status="FAIL",
                severity="HIGH",
                remediation_command="line vty 0 4\n transport input ssh",
                description="Insecure Telnet transport is permitted on VTY management lines.",
            ))

        # Check 3: Password Encryption (service password-encryption)
        total += 1
        if "service password-encryption" in config_text:
            passed += 1
            findings.append(CisFinding(
                check_id="CIS-3.1",
                title="Service Password Encryption",
                status="PASS",
                severity="MEDIUM",
                description="Cleartext password storage encryption service is enabled.",
            ))
        else:
            findings.append(CisFinding(
                check_id="CIS-3.1",
                title="Service Password Encryption",
                status="FAIL",
                severity="MEDIUM",
                remediation_command="service password-encryption",
                description="Passwords may be stored in plaintext within running-config.",
            ))

        # Check 4: SNMP Community String Security
        total += 1
        if "snmp-server community public" in config_text or "snmp-server community private" in config_text:
            findings.append(CisFinding(
                check_id="CIS-4.1",
                title="Default SNMP Community Strings",
                status="FAIL",
                severity="HIGH",
                remediation_command="no snmp-server community public\nno snmp-server community private",
                description="Default SNMP community strings ('public' or 'private') detected in config.",
            ))
        else:
            passed += 1
            findings.append(CisFinding(
                check_id="CIS-4.1",
                title="Default SNMP Community Strings",
                status="PASS",
                severity="HIGH",
                description="No default SNMP community strings found.",
            ))

        # Check 5: Logging / Syslog Remote Forwarding
        total += 1
        if "logging host" in config_text or "logging server" in config_text:
            passed += 1
            findings.append(CisFinding(
                check_id="CIS-5.1",
                title="Remote Syslog Forwarding",
                status="PASS",
                severity="MEDIUM",
                description="Remote centralized syslog collector configured.",
            ))
        else:
            findings.append(CisFinding(
                check_id="CIS-5.1",
                title="Remote Syslog Forwarding",
                status="FAIL",
                severity="MEDIUM",
                remediation_command="logging host 10.100.0.50",
                description="No remote syslog server configured; audit trail vulnerable to loss.",
            ))

        # Check 6: NTP Server Configuration
        total += 1
        if "ntp server" in config_text:
            passed += 1
            findings.append(CisFinding(
                check_id="CIS-6.1",
                title="Network Time Protocol (NTP)",
                status="PASS",
                severity="LOW",
                description="Authoritative NTP time synchronization configured.",
            ))
        else:
            findings.append(CisFinding(
                check_id="CIS-6.1",
                title="Network Time Protocol (NTP)",
                status="FAIL",
                severity="LOW",
                remediation_command="ntp server 10.100.0.100",
                description="NTP server missing; system clocks may drift.",
            ))

        score = round((passed / max(1, total)) * 100.0, 1)
        return score, findings
