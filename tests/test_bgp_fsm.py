"""
Unit tests for RFC 4271 BGP Finite State Machine (FSM).
"""

import pytest
from backend.app.routing.bgp_fsm import (
    BgpFiniteStateMachine,
    BgpPeerConfig,
    BgpState,
    BgpEvent,
)


def test_bgp_fsm_lifecycle():
    config = BgpPeerConfig(
        peer_ip="10.100.0.2",
        remote_as=65001,
        local_ip="10.100.0.1",
        local_as=65001,
    )
    fsm = BgpFiniteStateMachine(config)
    assert fsm.get_state() == BgpState.IDLE

    # Manual Start -> CONNECT
    st = fsm.handle_event(BgpEvent.MANUAL_START)
    assert st == BgpState.CONNECT

    # TCP Confirmed -> OPENSENT
    st = fsm.handle_event(BgpEvent.TCP_CONNECTION_CONFIRMED)
    assert st == BgpState.OPENSENT

    # BGP OPEN Received -> OPENCONFIRM (and sends Keepalive)
    st = fsm.handle_event(BgpEvent.BGP_OPEN_RECEIVED)
    assert st == BgpState.OPENCONFIRM
    assert fsm.stats.keepalives_sent_count == 1

    # BGP KEEPALIVE Received -> ESTABLISHED
    st = fsm.handle_event(BgpEvent.BGP_KEEPALIVE_RECEIVED)
    assert st == BgpState.ESTABLISHED
    assert fsm.stats.established_transitions == 1

    # BGP UPDATE Received with prefixes
    fsm.handle_event(BgpEvent.BGP_UPDATE_RECEIVED, payload={"prefixes": [{"prefix": "10.200.0.0/16", "next_hop": "10.100.0.2"}]})
    assert fsm.stats.prefixes_received_count == 1
    assert fsm.stats.updates_received_count == 1

    # Hold Timer Expired -> IDLE
    st = fsm.handle_event(BgpEvent.HOLD_TIMER_EXPIRED)
    assert st == BgpState.IDLE
    assert fsm.stats.drops_count == 1
    assert fsm.stats.prefixes_received_count == 0
