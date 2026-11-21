# DESI∞ INFINITY SYSTEM — Knowledge Reasoning Engine
# Version: 6.2.0
# Module: knowledge_reasoning_engine.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Knowledge Reasoning Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def infer_reachable(
    facts: list[tuple[str, str]],
    start: str
) -> list[str]:
    """Treat each fact as a directed relation (subject, object); no hidden inference."""
    graph = {}
    for subject, obj in facts:
        graph.setdefault(subject, set()).add(obj)

    seen = {start}
    stack = [start]

    while stack:
        node = stack.pop()
        for nxt in graph.get(node, ()):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)

    seen.remove(start)
    return sorted(seen)
