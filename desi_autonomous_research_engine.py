# DESI∞ INFINITY SYSTEM — Autonomous Research Workflow Engine
# Version: 6.2.0
# Module: desi_autonomous_research_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Autonomous Research Workflow Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

class ResearchWorkflow:
    """Plans and tracks research tasks; it does not independently validate discoveries."""

    def __init__(self):
        self.tasks = {}

    def add_task(
        self,
        task_id: str,
        description: str,
        dependencies: list[str] | None = None
    ) -> None:
        if not task_id or task_id in self.tasks:
            raise ValueError("Task ID must be unique and non-empty.")
        self.tasks[task_id] = {
            "description": description,
            "dependencies": list(dependencies or []),
            "status": "pending"
        }

    def set_status(self, task_id: str, status: str) -> None:
        allowed = {"pending", "running", "completed", "blocked"}
        if task_id not in self.tasks:
            raise KeyError(task_id)
        if status not in allowed:
            raise ValueError(f"Status must be one of {sorted(allowed)}.")
        self.tasks[task_id]["status"] = status

    def summary(self) -> dict:
        counts = {}
        for task in self.tasks.values():
            status = task["status"]
            counts[status] = counts.get(status, 0) + 1
        return {
            "task_count": len(self.tasks),
            "status_counts": counts,
            "tasks": self.tasks.copy()
        }
