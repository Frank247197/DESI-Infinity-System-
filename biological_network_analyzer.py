"""DESI Infinity System - Biological Network Analyzer (v6.2.0).

Generic biological network (nodes and edges) with graph queries:
neighbours, centrality, connected components, shortest path. Deterministic
in-memory implementation; no network inference.
"""
from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Set

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

NODE_TYPES = ("gene", "protein", "pathway", "disease", "compound",
              "metabolite", "other")
EDGE_TYPES = ("physical", "regulatory", "functional", "genetic",
              "association", "other")
SOURCES = ("curated", "literature", "predicted")


class NetworkAnalyzerError(Exception):
    """Base network analyzer error."""


@dataclass
class NetworkNode:
    node_id: str
    node_type: str = "other"
    label: str = ""

    def __post_init__(self) -> None:
        if not self.node_id or not isinstance(self.node_id, str):
            raise NetworkAnalyzerError("node_id required")
        if self.node_type not in NODE_TYPES:
            raise NetworkAnalyzerError(f"invalid node_type: {self.node_type!r}")


@dataclass
class NetworkEdge:
    source: str
    target: str
    edge_type: str = "other"
    weight: float = 1.0
    source_note: str = ""

    def __post_init__(self) -> None:
        if not self.source or not self.target:
            raise NetworkAnalyzerError("source and target required")
        if self.source == self.target:
            raise NetworkAnalyzerError("self-edges not allowed")
        if self.edge_type not in EDGE_TYPES:
            raise NetworkAnalyzerError(f"invalid edge_type: {self.edge_type!r}")
        if not isinstance(self.weight, (int, float)) or self.weight <= 0:
            raise NetworkAnalyzerError("weight must be a positive number")


class BiologicalNetworkAnalyzer:
    """Undirected biological network with standard graph queries."""

    def __init__(self) -> None:
        self._nodes: Dict[str, NetworkNode] = {}
        self._edges: List[NetworkEdge] = []
        self._adjacency: Dict[str, Dict[str, float]] = {}

    def add_node(self, node: NetworkNode) -> NetworkNode:
        if node.node_id in self._nodes:
            raise NetworkAnalyzerError(f"duplicate node_id: {node.node_id}")
        self._nodes[node.node_id] = node
        self._adjacency[node.node_id] = {}
        return node

    def add_edge(self, edge: NetworkEdge) -> NetworkEdge:
        for nid in (edge.source, edge.target):
            if nid not in self._nodes:
                raise NetworkAnalyzerError(f"unknown node_id: {nid}")
        self._edges.append(edge)
        self._adjacency[edge.source][edge.target] = edge.weight
        self._adjacency[edge.target][edge.source] = edge.weight
        return edge

    def get_node(self, node_id: str) -> NetworkNode:
        try:
            return self._nodes[node_id]
        except KeyError as exc:
            raise NetworkAnalyzerError(f"unknown node_id: {node_id}") from exc

    def neighbours(self, node_id: str) -> List[str]:
        self.get_node(node_id)
        return sorted(self._adjacency[node_id])

    def degree(self, node_id: str) -> int:
        return len(self.neighbours(node_id))

    def top_hubs(self, top_n: int = 5) -> List[Dict[str, object]]:
        if top_n <= 0:
            raise NetworkAnalyzerError("top_n must be positive")
        rows = [{"node_id": nid, "degree": self.degree(nid)}
                for nid in self._nodes]
        rows.sort(key=lambda r: r["degree"], reverse=True)  # type: ignore
        return rows[:top_n]

    def connected_components(self) -> List[Set[str]]:
        seen: Set[str] = set()
        comps: List[Set[str]] = []
        for nid in self._nodes:
            if nid in seen:
                continue
            comp: Set[str] = set()
            q = deque([nid])
            seen.add(nid)
            while q:
                current = q.popleft()
                comp.add(current)
                for nbr in self._adjacency[current]:
                    if nbr not in seen:
                        seen.add(nbr)
                        q.append(nbr)
            comps.append(comp)
        return comps

    def shortest_path(self, source: str, target: str) -> List[str]:
        if source not in self._nodes or target not in self._nodes:
            return []
        prev: Dict[str, str] = {}
        seen: Set[str] = {source}
        q = deque([source])
        while q:
            current = q.popleft()
            if current == target:
                path = [target]
                while path[-1] != source:
                    path.append(prev[path[-1]])
                return list(reversed(path))
            for nbr in self._adjacency[current]:
                if nbr not in seen:
                    seen.add(nbr)
                    prev[nbr] = current
                    q.append(nbr)
        return []

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "components": len(self.connected_components()),
        }


def self_test() -> bool:
    net = BiologicalNetworkAnalyzer()
    for nid, ntype in (("TP53", "gene"), ("MDM2", "gene"),
                       ("BAX", "gene"), ("AKT1", "gene"), ("MTOR", "gene")):
        net.add_node(NetworkNode(nid, ntype, nid))
    net.add_edge(NetworkEdge("TP53", "MDM2", "physical", 0.95))
    net.add_edge(NetworkEdge("TP53", "BAX", "regulatory", 0.9))
    net.add_edge(NetworkEdge("MDM2", "AKT1", "regulatory", 0.7))
    net.add_edge(NetworkEdge("AKT1", "MTOR", "physical", 0.85))
    assert net.neighbours("TP53") == ["BAX", "MDM2"]
    assert net.degree("TP53") == 2
    assert net.shortest_path("TP53", "MTOR") == ["TP53", "MDM2", "AKT1", "MTOR"]
    assert len(net.connected_components()) == 1
    assert net.top_hubs(1)[0]["node_id"] in ("TP53", "MDM2", "AKT1")
    print("biological_network_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
