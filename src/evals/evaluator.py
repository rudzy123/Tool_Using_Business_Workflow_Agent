from typing import Dict, Any

from src.evals.metrics import (
    extraction_accuracy,
    output_completeness,
    tool_success_rate,
)


class WorkflowEvaluator:
    """
    Runs evaluation metrics against a persisted workflow run.
    """

    def evaluate(self, run_payload: Dict[str, Any]) -> Dict[str, float]:
        extracted_skills = run_payload["extracted_skills"]["extracted_skills"]
        trace = run_payload["trace"]

        return {
            "extraction_accuracy": extraction_accuracy(extracted_skills),
            "output_completeness": output_completeness(run_payload),
            "tool_success_rate": tool_success_rate(trace),
        }