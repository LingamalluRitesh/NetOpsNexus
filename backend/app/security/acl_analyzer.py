"""
ACL Shadow and Redundancy Analyzer discovering shadowed and unreachable firewall/router access-list entries.
"""

from typing import List, Tuple, Dict, Any
import ipaddress
from backend.app.security.models import AclRule


class AclShadowAnalyzer:
    @staticmethod
    def _ip_is_subset(child_cidr: str, parent_cidr: str) -> bool:
        """Check if child IP/CIDR is completely covered by parent IP/CIDR."""
        if parent_cidr.lower() == "any":
            return True
        if child_cidr.lower() == "any":
            return False
        
        try:
            p_net = ipaddress.ip_network(parent_cidr, strict=False)
            c_net = ipaddress.ip_network(child_cidr, strict=False)
            return c_net.subnet_of(p_net)
        except Exception:
            return child_cidr == parent_cidr

    @staticmethod
    def _port_is_subset(child_port: str, parent_port: str) -> bool:
        """Check if child port is covered by parent port specification."""
        if parent_port.lower() == "any":
            return True
        if child_port.lower() == "any":
            return False
        return child_port == parent_port

    @staticmethod
    def analyze_acl(rules: List[AclRule]) -> List[AclRule]:
        """Inspect ordered ACL rules and mark shadowed entries."""
        # Sort rules by sequence number ascending
        sorted_rules = sorted(rules, key=lambda r: r.sequence_num)

        for i, curr_rule in enumerate(sorted_rules):
            curr_rule.is_shadowed = False
            curr_rule.shadowed_by_sequence = None

            # Compare against all prior rules in the list
            for prev_rule in sorted_rules[:i]:
                # 1. Check protocol match (or parent is 'ip')
                proto_match = (prev_rule.protocol == "ip") or (prev_rule.protocol == curr_rule.protocol)
                if not proto_match:
                    continue

                # 2. Check src IP subset
                src_match = AclShadowAnalyzer._ip_is_subset(curr_rule.src_ip_prefix, prev_rule.src_ip_prefix)
                if not src_match:
                    continue

                # 3. Check dst IP subset
                dst_match = AclShadowAnalyzer._ip_is_subset(curr_rule.dst_ip_prefix, prev_rule.dst_ip_prefix)
                if not dst_match:
                    continue

                # 4. Check ports
                src_p_match = AclShadowAnalyzer._port_is_subset(curr_rule.src_port, prev_rule.src_port)
                dst_p_match = AclShadowAnalyzer._port_is_subset(curr_rule.dst_port, prev_rule.dst_port)

                if src_p_match and dst_p_match:
                    # Current rule is completely shadowed by previous rule
                    curr_rule.is_shadowed = True
                    curr_rule.shadowed_by_sequence = prev_rule.sequence_num
                    break

        return sorted_rules
