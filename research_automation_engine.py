# DESI∞ INFINITY SYSTEM — Research Workflow Engine
# Version: 6.2.0
# Module: research_automation_engine.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Research Workflow Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def topological_order(tasks: dict[str, list[str]]) -> list[str]:
    """Return a valid dependency order or raise on missing dependencies/cycles."""
    for name, dependencies in tasks.items():
        missing = set(dependencies) - set(tasks)
        if missing:
            raise ValueError(
                f"{name} has unknown dependencies: {sorted(missing)}"
            )

    temporary = set()
    permanent = set()
    order = []

    def visit(node):
        if node in temporary:
            raise ValueError("Dependency cycle detected.")
        if node not in permanent:
            temporary.add(node)
            for dependency in tasks[node]:
                visit(dependency)
            temporary.remove(node)
            permanent.add(node)
            order.append(node)

    for name in tasks:
        visit(name)

    return order
