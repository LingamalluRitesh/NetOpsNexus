"""
RFC 4271 Border Gateway Protocol (BGP-4) Finite State Machine (FSM).
Implements all 6 standard BGP states:
- IDLE
- CONNECT
- ACTIVE
- OPENSENT
- OPENCONFIRM
- ESTABLISHED

Handles timers (ConnectRetry, HoldTime, Keepalive) and message exchanges (OPEN, KEEPALIVE, UPDATE, NOTIFICATION).
"""

from typing import Dict, Any, List, Optional, Tuple, Callable
from enum import Enum
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone


class BgpState(str, Enum):
    IDLE = "IDLE"
    CONNECT = "CONNECT"
    ACTIVE = "ACTIVE"
    OPENSENT = "OPENSENT"
    OPENCONFIRM = "OPENCONFIRM"
    ESTABLISHED = "ESTABLISHED"


class BgpEvent(str, Enum):
    MANUAL_START = "MANUAL_START"
    MANUAL_STOP = "MANUAL_STOP"
    CONNECT_RETRY_TIMER_EXPIRED = "CONNECT_RETRY_TIMER_EXPIRED"
    HOLD_TIMER_EXPIRED = "HOLD_TIMER_EXPIRED"
    KEEPALIVE_TIMER_EXPIRED = "KEEPALIVE_TIMER_EXPIRED"
    TCP_CONNECTION_CONFIRMED = "TCP_CONNECTION_CONFIRMED"
    TCP_CONNECTION_FAILS = "TCP_CONNECTION_FAILS"
    BGP_OPEN_RECEIVED = "BGP_OPEN_RECEIVED"
    BGP_HEADER_ERR = "BGP_HEADER_ERR"
    BGP_OPEN_MSG_ERR = "BGP_OPEN_MSG_ERR"
    BGP_KEEPALIVE_RECEIVED = "BGP_KEEPALIVE_RECEIVED"
    BGP_UPDATE_RECEIVED = "BGP_UPDATE_RECEIVED"
    BGP_NOTIFICATION_RECEIVED = "BGP_NOTIFICATION_RECEIVED"


@dataclass
class BgpPeerConfig:
    peer_ip: str
    remote_as: int
    local_ip: str
    local_as: int
    hold_time_seconds: int = 90
    keepalive_time_seconds: int = 30
    connect_retry_time_seconds: int = 120
    is_passive: bool = False


@dataclass
class BgpSessionStats:
    state: BgpState = BgpState.IDLE
    established_transitions: int = 0
    drops_count: int = 0
    prefixes_received_count: int = 0
    prefixes_advertised_count: int = 0
    updates_received_count: int = 0
    updates_sent_count: int = 0
    keepalives_sent_count: int = 0
    keepalives_received_count: int = 0
    last_state_change: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BgpFiniteStateMachine:
    """Stateful BGP-4 Neighbor Session Engine."""

    def __init__(self, config: BgpPeerConfig):
        self.config = config
        self.stats = BgpSessionStats()
        self.routes_rib_in: List[Dict[str, Any]] = []
        self.routes_rib_out: List[Dict[str, Any]] = []

    def get_state(self) -> BgpState:
        return self.stats.state

    def transition_to(self, new_state: BgpState):
        """Execute state transition and update telemetry counters."""
        old_state = self.stats.state
        self.stats.state = new_state
        self.stats.last_state_change = datetime.now(timezone.utc)
        if new_state == BgpState.ESTABLISHED:
            self.stats.established_transitions += 1
        elif old_state == BgpState.ESTABLISHED and new_state != BgpState.ESTABLISHED:
            self.stats.drops_count += 1

    def handle_event(self, event: BgpEvent, payload: Optional[Dict[str, Any]] = None) -> BgpState:
        """Process RFC 4271 BGP FSM state machine event."""
        current = self.stats.state

        # IDLE State
        if current == BgpState.IDLE:
            if event == BgpEvent.MANUAL_START:
                self.transition_to(BgpState.CONNECT)

        # CONNECT State
        elif current == BgpState.CONNECT:
            if event == BgpEvent.TCP_CONNECTION_CONFIRMED:
                self.transition_to(BgpState.OPENSENT)
            elif event in (BgpEvent.TCP_CONNECTION_FAILS, BgpEvent.CONNECT_RETRY_TIMER_EXPIRED):
                self.transition_to(BgpState.ACTIVE)
            elif event == BgpEvent.MANUAL_STOP:
                self.transition_to(BgpState.IDLE)

        # ACTIVE State
        elif current == BgpState.ACTIVE:
            if event == BgpEvent.TCP_CONNECTION_CONFIRMED:
                self.transition_to(BgpState.OPENSENT)
            elif event == BgpEvent.CONNECT_RETRY_TIMER_EXPIRED:
                self.transition_to(BgpState.CONNECT)
            elif event == BgpEvent.MANUAL_STOP:
                self.transition_to(BgpState.IDLE)

        # OPENSENT State
        elif current == BgpState.OPENSENT:
            if event == BgpEvent.BGP_OPEN_RECEIVED:
                self.stats.keepalives_sent_count += 1
                self.transition_to(BgpState.OPENCONFIRM)
            elif event in (BgpEvent.BGP_HEADER_ERR, BgpEvent.BGP_OPEN_MSG_ERR, BgpEvent.TCP_CONNECTION_FAILS):
                self.transition_to(BgpState.IDLE)
            elif event == BgpEvent.HOLD_TIMER_EXPIRED:
                self.transition_to(BgpState.IDLE)

        # OPENCONFIRM State
        elif current == BgpState.OPENCONFIRM:
            if event == BgpEvent.BGP_KEEPALIVE_RECEIVED:
                self.transition_to(BgpState.ESTABLISHED)
            elif event in (BgpEvent.HOLD_TIMER_EXPIRED, BgpEvent.BGP_NOTIFICATION_RECEIVED, BgpEvent.TCP_CONNECTION_FAILS):
                self.transition_to(BgpState.IDLE)

        # ESTABLISHED State
        elif current == BgpState.ESTABLISHED:
            if event == BgpEvent.BGP_KEEPALIVE_RECEIVED:
                self.stats.keepalives_received_count += 1
            elif event == BgpEvent.BGP_UPDATE_RECEIVED:
                self.stats.updates_received_count += 1
                if payload and "prefixes" in payload:
                    self.routes_rib_in.extend(payload["prefixes"])
                    self.stats.prefixes_received_count = len(self.routes_rib_in)
            elif event in (BgpEvent.HOLD_TIMER_EXPIRED, BgpEvent.BGP_NOTIFICATION_RECEIVED, BgpEvent.TCP_CONNECTION_FAILS, BgpEvent.MANUAL_STOP):
                self.routes_rib_in.clear()
                self.stats.prefixes_received_count = 0
                self.transition_to(BgpState.IDLE)

        return self.stats.state
