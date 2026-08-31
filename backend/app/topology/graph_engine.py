"""
Graph analysis engine leveraging NetworkX for network topology modeling,
Dijkstra shortest path tracing, SPOF articulation points, and blast radius calculation.
"""

from typing import List, Dict, Any, Tuple, Optional, Set
import networkx as nx
from backend.app.topology.schemas import (
    TopologyNodeResponse, TopologyEdgeResponse, TopologyGraphResponse,
    PathHop, PathTraceResponse, DependencyAnalysisResponse, SpofReportResponse
)


class TopologyGraphEngine:
    def __init__(self, nodes: List[TopologyNodeResponse], edges: List[TopologyEdgeResponse]):
        self.nodes_map: Dict[int, TopologyNodeResponse] = {n.device_id: n for n in nodes}
        self.edges_list = edges
        
        # Build NetworkX MultiGraph
        self.G = nx.Graph()
        self.DiG = nx.DiGraph()

        for node in nodes:
            self.G.add_node(
                node.device_id,
                hostname=node.hostname,
                ip=node.management_ip,
                device_type=node.device_type.value,
                status=node.status.value,
                site_id=node.site_id,
            )
            self.DiG.add_node(
                node.device_id,
                hostname=node.hostname,
                ip=node.management_ip,
                device_type=node.device_type.value,
                status=node.status.value,
                site_id=node.site_id,
            )

        for edge in edges:
            weight_latency = edge.latency_ms + (edge.packet_loss_pct * 10.0)
            self.G.add_edge(
                edge.source_device_id,
                edge.target_device_id,
                link_id=edge.link_id,
                weight=max(0.1, weight_latency),
                latency_ms=edge.latency_ms,
                loss_pct=edge.packet_loss_pct,
                bandwidth_mbps=edge.bandwidth_mbps,
                utilization_pct=edge.utilization_pct,
                source_if=edge.source_interface_name,
                target_if=edge.target_interface_name,
                status=edge.status.value,
            )
            self.DiG.add_edge(
                edge.source_device_id,
                edge.target_device_id,
                weight=max(0.1, weight_latency),
                link_id=edge.link_id,
                latency_ms=edge.latency_ms,
                loss_pct=edge.packet_loss_pct,
                bandwidth_mbps=edge.bandwidth_mbps,
                utilization_pct=edge.utilization_pct,
                source_if=edge.source_interface_name,
                target_if=edge.target_interface_name,
            )

    def trace_path(self, source_id: int, target_id: int, optimize_for: str = "latency") -> PathTraceResponse:
        """Find optimal shortest path and redundant backup paths using Dijkstra algorithm."""
        src_node = self.nodes_map.get(source_id)
        dst_node = self.nodes_map.get(target_id)

        if not src_node or not dst_node:
            return PathTraceResponse(
                source_hostname=src_node.hostname if src_node else "Unknown",
                target_hostname=dst_node.hostname if dst_node else "Unknown",
                is_path_found=False,
                total_hops=0,
                total_latency_ms=0.0,
                accumulated_loss_pct=100.0,
                min_bottleneck_bandwidth_mbps=0,
                primary_path=[],
                redundant_paths=[],
            )

        if not nx.has_path(self.G, source_id, target_id):
            return PathTraceResponse(
                source_hostname=src_node.hostname,
                target_hostname=dst_node.hostname,
                is_path_found=False,
                total_hops=0,
                total_latency_ms=0.0,
                accumulated_loss_pct=100.0,
                min_bottleneck_bandwidth_mbps=0,
                primary_path=[],
                redundant_paths=[],
            )

        # Primary shortest path
        path_node_ids = nx.shortest_path(self.G, source=source_id, target=target_id, weight="weight")
        primary_hops: List[PathHop] = []
        total_latency = 0.0
        total_loss = 0.0
        min_bw = 1000000

        for idx, dev_id in enumerate(path_node_ids):
            node_obj = self.nodes_map[dev_id]
            hop_latency = 0.0
            hop_loss = 0.0
            hop_util = 0.0
            ing_if = None
            egr_if = None

            if idx > 0:
                prev_id = path_node_ids[idx - 1]
                edge_data = self.G.get_edge_data(prev_id, dev_id)
                if edge_data:
                    hop_latency = edge_data.get("latency_ms", 0.5)
                    hop_loss = edge_data.get("loss_pct", 0.0)
                    hop_util = edge_data.get("utilization_pct", 0.0)
                    ing_if = edge_data.get("target_if")
                    egr_if = edge_data.get("source_if")
                    bw = edge_data.get("bandwidth_mbps", 1000)
                    min_bw = min(min_bw, bw)

            total_latency += hop_latency
            total_loss += hop_loss

            primary_hops.append(
                PathHop(
                    hop_number=idx + 1,
                    device_id=dev_id,
                    hostname=node_obj.hostname,
                    management_ip=node_obj.management_ip,
                    device_type=node_obj.device_type.value,
                    ingress_interface=ing_if,
                    egress_interface=egr_if,
                    link_latency_ms=round(hop_latency, 2),
                    link_loss_pct=round(hop_loss, 2),
                    link_utilization_pct=round(hop_util, 1),
                )
            )

        # Compute redundant paths using k-shortest simple paths
        redundant_hops_list: List[List[PathHop]] = []
        try:
            simple_paths = list(nx.shortest_simple_paths(self.G, source_id, target_id, weight="weight"))
            for alt_path in simple_paths[1:3]:  # up to 2 alternate paths
                alt_hops = []
                for idx, dev_id in enumerate(alt_path):
                    node_obj = self.nodes_map[dev_id]
                    alt_hops.append(
                        PathHop(
                            hop_number=idx + 1,
                            device_id=dev_id,
                            hostname=node_obj.hostname,
                            management_ip=node_obj.management_ip,
                            device_type=node_obj.device_type.value,
                            link_latency_ms=0.5,
                            link_loss_pct=0.0,
                            link_utilization_pct=0.0,
                        )
                    )
                redundant_hops_list.append(alt_hops)
        except Exception:
            pass

        return PathTraceResponse(
            source_hostname=src_node.hostname,
            target_hostname=dst_node.hostname,
            is_path_found=True,
            total_hops=len(primary_hops),
            total_latency_ms=round(total_latency, 2),
            accumulated_loss_pct=round(total_loss, 2),
            min_bottleneck_bandwidth_mbps=min_bw if min_bw != 1000000 else 1000,
            primary_path=primary_hops,
            redundant_paths=redundant_hops_list,
        )

    def analyze_dependencies(self, device_id: int) -> DependencyAnalysisResponse:
        """Compute upstream core dependencies, downstream blast radius, and SPOF assessment."""
        target_node = self.nodes_map.get(device_id)
        if not target_node:
            raise ValueError(f"Device {device_id} not found in topology graph")

        # 1. Identify upstream dependencies (nodes with higher hierarchy / core roles)
        upstream_nodes: List[TopologyNodeResponse] = []
        downstream_nodes: List[TopologyNodeResponse] = []
        
        # Check articulation points (SPOF)
        articulation_points = set(nx.articulation_points(self.G))
        is_spof = device_id in articulation_points

        # Calculate blast radius by removing node and checking disconnected components
        G_temp = self.G.copy()
        G_temp.remove_node(device_id)
        
        # Nodes that lost connectivity to core routers
        core_nodes = [n.device_id for n in self.nodes_map.values() if "core" in n.device_type.value or "spine" in n.device_type.value]
        disconnected_nodes = set()

        if core_nodes:
            primary_core = core_nodes[0]
            if primary_core in G_temp:
                reachable_from_core = set(nx.node_connected_component(G_temp, primary_core))
                for node_id in self.nodes_map:
                    if node_id != device_id and node_id not in reachable_from_core:
                        disconnected_nodes.add(node_id)
        
        for nid in disconnected_nodes:
            if nid in self.nodes_map:
                downstream_nodes.append(self.nodes_map[nid])

        # Neighbors
        neighbors = set(self.G.neighbors(device_id))
        for nid in neighbors:
            n_obj = self.nodes_map[nid]
            if "core" in n_obj.device_type.value or "spine" in n_obj.device_type.value:
                upstream_nodes.append(n_obj)

        affected_sites = list(set([n.site_id for n in downstream_nodes if n.site_id is not None]))
        if target_node.site_id:
            affected_sites.append(target_node.site_id)
            affected_sites = list(set(affected_sites))

        severity = "low"
        if is_spof or len(downstream_nodes) > 5:
            severity = "critical"
        elif len(downstream_nodes) > 1:
            severity = "high"
        elif "core" in target_node.device_type.value:
            severity = "critical"

        return DependencyAnalysisResponse(
            target_device_id=device_id,
            hostname=target_node.hostname,
            upstream_dependencies=upstream_nodes,
            downstream_impact=downstream_nodes,
            affected_site_ids=affected_sites,
            blast_radius_device_count=len(downstream_nodes) + 1,
            is_single_point_of_failure=is_spof,
            impact_severity=severity,
        )

    def detect_spof_report(self) -> SpofReportResponse:
        """Find all Single Points of Failure and Critical Bridge Links across the network."""
        art_points = set(nx.articulation_points(self.G))
        spof_nodes = [self.nodes_map[nid] for nid in art_points if nid in self.nodes_map]

        bridges = list(nx.bridges(self.G))
        critical_edges = []
        for u, v in bridges:
            matching_edge = next((e for e in self.edges_list if (e.source_device_id == u and e.target_device_id == v) or (e.source_device_id == v and e.target_device_id == u)), None)
            if matching_edge:
                critical_edges.append(matching_edge)

        # Health score: 100 - penalties for SPOFs
        total_nodes = len(self.nodes_map)
        score = max(20.0, 100.0 - (len(spof_nodes) * 8.0) - (len(critical_edges) * 4.0))

        return SpofReportResponse(
            single_points_of_failure=spof_nodes,
            critical_bridge_links=critical_edges,
            network_connectivity_score=round(score, 1),
        )
