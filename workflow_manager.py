# ============================================================
# DESI∞ INFINITY SYSTEM 6.2.0 - RESEARCH WORKFLOW MANAGER
# Pipeline Sequencing, Validation Checkpoints & Provenance Records
# ============================================================

from typing import Dict, Any, List, Callable

class ResearchWorkflowManager:
    """
    [CALC] Organizes multi-step scientific computations into repeatable 
    pipelines with defined validation checkpoints and intermediate result logging.
    """
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, step_name: str, func: Callable, validator: Callable = None) -> None:
        self.steps.append({"name": step_name, "func": func, "validator": validator})

    def execute_pipeline(self, initial_input: Any) -> Dict[str, Any]:
        current_data = initial_input
        execution_history = []

        for step in self.steps:
            try:
                current_data = step["func"](current_data)
                if step["validator"] and not step["validator"](current_data):
                    raise ValueError(f"Checkpoint validation failed at step: {step['name']}")
                execution_history.append({"step": step["name"], "status": "PASSED"})
            except Exception as e:
                return {
                    "workflow": self.workflow_name,
                    "status": "FAILED",
                    "failed_step": step["name"],
                    "error": str(e),
                    "history": execution_history
                }

        return {
            "workflow": self.workflow_name,
            "status": "COMPLETED_SUCCESS",
            "final_output": current_data,
            "history": execution_history
        }

if __name__ == "__main__":
    wf = ResearchWorkflowManager("Genomic_Pipeline")
    wf.add_step("double_length", lambda x: x * 2, validator=lambda x: x > 0)
    print("Workflow Execution:", wf.execute_pipeline(5))
