# DESI∞ INFINITY SYSTEM — Systems Biology
# Version: 6.2.0
# Module: systems_biology.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Systems Biology"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def analyze_network(nodes: list[str], edges: list[tuple[str, str]]) -> dict:
    """Return node degrees, connected components, and graph density."""
    graph = {str(n): set() for n in nodes}
    if len(graph) != len(nodes):
        raise ValueError("Node identifiers must be unique.")
    for left, right in edges:
        if left not in graph or right not in graph:
            raise ValueError(f"Unknown endpoint in edge {(left, right)!r}.")
        if left == right:
            raise ValueError("Self-interactions are not accepted.")
        graph[left].add(right)
        graph[right].add(left)
    degrees = {node: len(neighbors) for node, neighbors in graph.items()}
    components, unseen = [], set(graph)
    while unseen:
        start = unseen.pop()
        stack = [start]
        component = {start}
        while stack:
            current = stack.pop()
            for neighbor in graph[current] & unseen:
                unseen.remove(neighbor)
                component.add(neighbor)
                stack.append(neighbor)
        components.append(sorted(component))
    possible = len(graph) * (len(graph) - 1) / 2
    actual = sum(degrees.values()) / 2
    return {
        "degrees": degrees,
        "components": components,
        "density": actual / possible if possible else 0.0
    }
