from typing import Dict


def format_eval_report(scores: Dict[str, float]) -> str:
    """
    Format evaluation scores as a readable report.
    """
    lines = ["Workflow Evaluation Report", "-" * 30]

    for metric, score in scores.items():
        lines.append(f"{metric}: {score:.2f}")

    return "\n".join(lines)