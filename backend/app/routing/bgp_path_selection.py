"""
BGP Best Path Selection Algorithm (RFC 4271 compliant).
Evaluates multiple candidate paths for the same prefix and selects the optimal path:
1. Highest Weight (Cisco proprietary)
2. Highest Local Preference
3. Locally originated over BGP learned
4. Shortest AS-Path length (ignoring AS-SET)
5. Lowest Origin code (IGP < EGP < Incomplete)
6. Lowest Multi-Exit Discriminator (MED)
7. eBGP path over iBGP path
8. Lowest IGP metric to Next-Hop
9. Lowest BGP Router ID (RID)
10. Lowest Neighbor IP address
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class BgpOrigin(int, Enum):
    IGP = 0
    EGP = 1
    INCOMPLETE = 2


@dataclass
class BgpPath:
    prefix: str
    next_hop: str
    weight: int = 0
    local_pref: int = 100
    is_local: bool = False
    as_path: List[int] = field(default_factory=list)
    origin: BgpOrigin = BgpOrigin.IGP
    med: int = 0
    is_ebgp: bool = True
    igp_cost_to_nexthop: int = 10
    router_id: str = "10.0.0.1"
    neighbor_ip: str = "10.0.0.2"


class BgpPathSelector:
    """Best Path Selection Evaluator."""

    @staticmethod
    def select_best_path(candidates: List[BgpPath]) -> Optional[BgpPath]:
        """Determine winning BGP path among candidates."""
        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]

        best = candidates[0]
        for candidate in candidates[1:]:
            best = BgpPathSelector._compare_two_paths(best, candidate)
        return best

    @staticmethod
    def _compare_two_paths(a: BgpPath, b: BgpPath) -> BgpPath:
        # 1. Weight (Highest wins)
        if a.weight != b.weight:
            return a if a.weight > b.weight else b

        # 2. Local Preference (Highest wins)
        if a.local_pref != b.local_pref:
            return a if a.local_pref > b.local_pref else b

        # 3. Locally Originated
        if a.is_local != b.is_local:
            return a if a.is_local else b

        # 4. AS-Path Length (Shortest wins)
        if len(a.as_path) != len(b.as_path):
            return a if len(a.as_path) < len(b.as_path) else b

        # 5. Origin (Lowest code: IGP(0) < EGP(1) < INCOMPLETE(2))
        if a.origin != b.origin:
            return a if a.origin.value < b.origin.value else b

        # 6. MED (Lowest wins)
        if a.med != b.med:
            return a if a.med < b.med else b

        # 7. eBGP over iBGP
        if a.is_ebgp != b.is_ebgp:
            return a if a.is_ebgp else b

        # 8. Lowest IGP cost to next hop
        if a.igp_cost_to_nexthop != b.igp_cost_to_nexthop:
            return a if a.igp_cost_to_nexthop < b.igp_cost_to_nexthop else b

        # 9. Lowest Router ID
        a_rid_int = int("".join(f"{int(o):03d}" for o in a.router_id.split(".")))
        b_rid_int = int("".join(f"{int(o):03d}" for o in b.router_id.split(".")))
        if a_rid_int != b_rid_int:
            return a if a_rid_int < b_rid_int else b

        # 10. Lowest Neighbor IP
        a_nbr_int = int("".join(f"{int(o):03d}" for o in a.neighbor_ip.split(".")))
        b_nbr_int = int("".join(f"{int(o):03d}" for o in b.neighbor_ip.split(".")))
        return a if a_nbr_int <= b_nbr_int else b
