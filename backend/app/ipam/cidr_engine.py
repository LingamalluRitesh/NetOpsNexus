"""
High-performance IPAM CIDR calculation engine supporting IPv4/IPv6 subnetting,
prefix splitting, contiguous block merging, and host range derivation.
"""

from typing import List, Dict, Any, Tuple
import ipaddress
import netaddr
from backend.app.ipam.schemas import CidrCalculationResponse


class CidrEngine:
    @staticmethod
    def calculate_cidr(cidr_str: str) -> CidrCalculationResponse:
        """Calculate complete network parameters from CIDR string."""
        net = ipaddress.ip_network(cidr_str, strict=False)
        is_v4 = net.version == 4

        if is_v4:
            net_v4 = netaddr.IPNetwork(cidr_str)
            broadcast = str(net.broadcast_address)
            netmask = str(net.netmask)
            wildcard = str(net_v4.hostmask)
            total = net.num_addresses
            usable = max(0, total - 2) if net.prefixlen < 31 else total
            hosts = list(net.hosts())
            first_ip = str(hosts[0]) if hosts else str(net.network_address)
            last_ip = str(hosts[-1]) if hosts else str(net.broadcast_address)
        else:
            broadcast = "N/A (IPv6)"
            netmask = str(net.netmask)
            wildcard = "N/A (IPv6)"
            total = net.num_addresses
            usable = total
            first_ip = str(net.network_address)
            last_ip = str(net[-1])

        return CidrCalculationResponse(
            cidr=str(net),
            network_address=str(net.network_address),
            broadcast_address=broadcast,
            netmask=netmask,
            wildcard_mask=wildcard,
            prefix_len=net.prefixlen,
            ip_version=net.version,
            total_addresses=total,
            usable_hosts=usable,
            first_usable_ip=first_ip,
            last_usable_ip=last_ip,
            is_private=net.is_private,
        )

    @staticmethod
    def split_subnet(network_cidr: str, target_prefix_len: int) -> List[str]:
        """Split a subnet into smaller contiguous subnets of target prefix length."""
        parent_net = ipaddress.ip_network(network_cidr, strict=False)
        if target_prefix_len <= parent_net.prefixlen:
            raise ValueError(f"Target prefix length /{target_prefix_len} must be strictly greater than parent /{parent_net.prefixlen}")
        if target_prefix_len > (32 if parent_net.version == 4 else 128):
            raise ValueError(f"Target prefix length /{target_prefix_len} exceeds max bits for IP version {parent_net.version}")

        subnets = list(parent_net.subnets(new_prefix=target_prefix_len))
        return [str(s) for s in subnets]

    @staticmethod
    def merge_subnets(cidr_list: List[str]) -> List[str]:
        """Merge a list of adjacent subnets into supernets where possible."""
        ip_nets = [netaddr.IPNetwork(c) for c in cidr_list]
        merged = netaddr.cidr_merge(ip_nets)
        return [str(m) for m in merged]

    @staticmethod
    def get_next_available_ip(network_cidr: str, used_ips: List[str]) -> str:
        """Find first unallocated usable IP address within subnet."""
        net = ipaddress.ip_network(network_cidr, strict=False)
        used_set = set(used_ips)
        for host_ip in net.hosts():
            ip_str = str(host_ip)
            if ip_str not in used_set:
                return ip_str
        raise ValueError(f"No available IP addresses left in subnet {network_cidr}")
