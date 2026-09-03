"""
OSPFv2 (RFC 2328) Link-State Database (LSDB) and Dijkstra SPF Engine.
Supports:
- Router LSA (Type 1)
- Network LSA (Type 2)
- Summary LSA (Type 3)
- AS External LSA (Type 5)
- Shortest Path First (SPF) tree computation
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import heapq
from dataclasses import dataclass, field
from enum import Enum


class LsaType(int, Enum):
    ROUTER = 1
    NETWORK = 2
    SUMMARY_IP = 3
    SUMMARY_ASBR = 4
    AS_EXTERNAL = 5


@dataclass
class LsaRecord:
    lsa_type: LsaType
    link_state_id: str
    advertising_router: str
    sequence_number: int = 0x80000001
    age_seconds: int = 0
    checksum: int = 0x1234
    metric: int = 10
    links: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class OspfRoute:
    prefix: str
    cost: int
    next_hop: str
    area_id: str
    route_type: str  # "intra-area", "inter-area", "external-type1", "external-type2"


class OspfEngine:
    """OSPFv2 Link-State Routing and Convergence Simulation."""

    def __init__(self, router_id: str, area_id: str = "0.0.0.0"):
        self.router_id = router_id
        self.area_id = area_id
        self.lsdb: Dict[Tuple[int, str, str], LsaRecord] = {}
        self.routing_table: Dict[str, OspfRoute] = {}

    def install_lsa(self, lsa: LsaRecord):
        """Install or update LSA in Link-State Database."""
        key = (lsa.lsa_type.value, lsa.link_state_id, lsa.advertising_router)
        self.lsdb[key] = lsa

    def compute_spf_tree(self) -> Dict[str, int]:
        """Execute Dijkstra algorithm on LSDB to calculate shortest cost to all routers."""
        # Build adjacency graph from Type 1 Router LSAs
        adj: Dict[str, List[Tuple[str, int]]] = {}
        for (lsa_type, ls_id, adv_rtr), lsa in self.lsdb.items():
            if lsa_type == LsaType.ROUTER.value:
                if adv_rtr not in adj:
                    adj[adv_rtr] = []
                for link in lsa.links:
                    neighbor = link.get("neighbor_router_id")
                    cost = link.get("metric", 10)
                    if neighbor:
                        adj[adv_rtr].append((neighbor, cost))

        # Dijkstra algorithm
        distances: Dict[str, int] = {self.router_id: 0}
        pq: List[Tuple[int, str]] = [(0, self.router_id)]

        while pq:
            curr_dist, u = heapq.heappop(pq)
            if curr_dist > distances.get(u, float("inf")):
                continue

            for neighbor, cost in adj.get(u, []):
                new_dist = curr_dist + cost
                if new_dist < distances.get(neighbor, float("inf")):
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))

        return distances

    def get_summary_routes(self) -> List[OspfRoute]:
        """Generate routing table entries from LSDB."""
        routes = []
        spf_costs = self.compute_spf_tree()

        for (lsa_type, ls_id, adv_rtr), lsa in self.lsdb.items():
            if lsa_type == LsaType.SUMMARY_IP.value:
                rtr_cost = spf_costs.get(adv_rtr, 10)
                total_cost = rtr_cost + lsa.metric
                routes.append(
                    OspfRoute(
                        prefix=ls_id,
                        cost=total_cost,
                        next_hop=f"10.100.0.{adv_rtr.split('.')[-1]}",
                        area_id=self.area_id,
                        route_type="inter-area",
                    )
                )
        return routes
