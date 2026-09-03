"""
Unit tests for BGP Best Path Selection Algorithm.
"""

import pytest
from backend.app.routing.bgp_path_selection import BgpPathSelector, BgpPath, BgpOrigin


def test_bgp_path_selection_weight():
    p1 = BgpPath(prefix="192.168.1.0/24", next_hop="10.0.0.1", weight=100)
    p2 = BgpPath(prefix="192.168.1.0/24", next_hop="10.0.0.2", weight=200)
    best = BgpPathSelector.select_best_path([p1, p2])
    assert best.next_hop == "10.0.0.2"


def test_bgp_path_selection_local_pref():
    p1 = BgpPath(prefix="192.168.1.0/24", next_hop="10.0.0.1", local_pref=200)
    p2 = BgpPath(prefix="192.168.1.0/24", next_hop="10.0.0.2", local_pref=100)
    best = BgpPathSelector.select_best_path([p1, p2])
    assert best.next_hop == "10.0.0.1"


def test_bgp_path_selection_as_path_length():
    p1 = BgpPath(prefix="192.168.1.0/24", next_hop="10.0.0.1", as_path=[65001, 65002, 65003])
    p2 = BgpPath(prefix="192.168.1.0/24", next_hop="10.0.0.2", as_path=[65001, 65004])
    best = BgpPathSelector.select_best_path([p1, p2])
    assert best.next_hop == "10.0.0.2"


def test_bgp_path_selection_origin_and_med():
    # IGP vs INCOMPLETE
    p1 = BgpPath(prefix="192.168.1.0/24", next_hop="10.0.0.1", origin=BgpOrigin.IGP)
    p2 = BgpPath(prefix="192.168.1.0/24", next_hop="10.0.0.2", origin=BgpOrigin.INCOMPLETE)
    best = BgpPathSelector.select_best_path([p1, p2])
    assert best.next_hop == "10.0.0.1"

    # MED (lower is better)
    p3 = BgpPath(prefix="192.168.1.0/24", next_hop="10.0.0.3", med=50)
    p4 = BgpPath(prefix="192.168.1.0/24", next_hop="10.0.0.4", med=100)
    best = BgpPathSelector.select_best_path([p3, p4])
    assert best.next_hop == "10.0.0.3"
