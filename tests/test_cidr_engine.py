"""
Unit tests for IPAM CIDR calculations, subnet splitting, and subnet merging.
"""

import pytest
from backend.app.ipam.cidr_engine import CidrEngine


def test_cidr_calculation_ipv4():
    res = CidrEngine.calculate_cidr("10.20.10.0/24")
    assert res.network_address == "10.20.10.0"
    assert res.broadcast_address == "10.20.10.255"
    assert res.netmask == "255.255.255.0"
    assert res.prefix_len == 24
    assert res.total_addresses == 256
    assert res.usable_hosts == 254
    assert res.first_usable_ip == "10.20.10.1"
    assert res.last_usable_ip == "10.20.10.254"
    assert res.is_private is True


def test_subnet_splitting():
    # Split /24 into two /25s
    subnets_25 = CidrEngine.split_subnet("10.20.10.0/24", 25)
    assert len(subnets_25) == 2
    assert subnets_25 == ["10.20.10.0/25", "10.20.10.128/25"]

    # Split /24 into four /26s
    subnets_26 = CidrEngine.split_subnet("10.20.10.0/24", 26)
    assert len(subnets_26) == 4
    assert subnets_26 == ["10.20.10.0/26", "10.20.10.64/26", "10.20.10.128/26", "10.20.10.192/26"]


def test_subnet_merging():
    # Merge two contiguous /25s into /24
    merged = CidrEngine.merge_subnets(["10.20.10.0/25", "10.20.10.128/25"])
    assert len(merged) == 1
    assert str(merged[0]) == "10.20.10.0/24"


def test_next_available_ip():
    used = ["10.20.10.1", "10.20.10.2", "10.20.10.3"]
    next_ip = CidrEngine.get_next_available_ip("10.20.10.0/24", used)
    assert next_ip == "10.20.10.4"
