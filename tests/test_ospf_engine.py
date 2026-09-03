"""
Unit tests for OSPFv2 LSDB and Shortest Path First (SPF) Dijkstra Engine.
"""

import pytest
from backend.app.routing.ospf_engine import OspfEngine, LsaRecord, LsaType, OspfRoute


def test_ospf_spf_computation():
    engine = OspfEngine(router_id="10.100.0.1", area_id="0.0.0.0")

    # Install Type 1 Router LSAs forming a triangle network: R1 - R2 - R3
    # R1 (10.100.0.1) -> R2 (cost 10), R3 (cost 50)
    lsa_r1 = LsaRecord(
        lsa_type=LsaType.ROUTER,
        link_state_id="10.100.0.1",
        advertising_router="10.100.0.1",
        links=[
            {"neighbor_router_id": "10.100.0.2", "metric": 10},
            {"neighbor_router_id": "10.100.0.3", "metric": 50},
        ],
    )
    # R2 (10.100.0.2) -> R1 (cost 10), R3 (cost 15)
    lsa_r2 = LsaRecord(
        lsa_type=LsaType.ROUTER,
        link_state_id="10.100.0.2",
        advertising_router="10.100.0.2",
        links=[
            {"neighbor_router_id": "10.100.0.1", "metric": 10},
            {"neighbor_router_id": "10.100.0.3", "metric": 15},
        ],
    )
    # R3 (10.100.0.3) -> R1 (cost 50), R2 (cost 15)
    lsa_r3 = LsaRecord(
        lsa_type=LsaType.ROUTER,
        link_state_id="10.100.0.3",
        advertising_router="10.100.0.3",
        links=[
            {"neighbor_router_id": "10.100.0.1", "metric": 50},
            {"neighbor_router_id": "10.100.0.2", "metric": 15},
        ],
    )

    engine.install_lsa(lsa_r1)
    engine.install_lsa(lsa_r2)
    engine.install_lsa(lsa_r3)

    spf_costs = engine.compute_spf_tree()

    # Cost to R1 is 0
    assert spf_costs["10.100.0.1"] == 0
    # Cost to R2 is 10
    assert spf_costs["10.100.0.2"] == 10
    # Cost to R3 via R2 is 10 + 15 = 25 (cheaper than direct link 50)
    assert spf_costs["10.100.0.3"] == 25
