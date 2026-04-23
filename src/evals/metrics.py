from typing import Dict, Any, List


def extraction_accuracy(extracted_skills: List[Dict[str, Any]]) -> float:
    """
    Measures whether skill extraction produced a non-empty,
    well-structured result.
    """
    if not extracted_skills:
        return 0.0

    valid = [
        s for s in extracted_skills
        if "name" in s and isinstance(s.get("importance"), float)
    ]

    return len(valid) / len(extracted_skills)


def output_completeness(run_output: Dict[str, Any]) -> float:
    """
    Checks whether required workflow outputs are present.
    """
    required_fields = [
        "job_description",
        "extracted_skills",
        "resume_comparison",
        "resume_edit_suggestions",
        "cover_letter_bullets",
        "outreach_draft",
    ]

    present = [f for f in required_fields if f in run_output]
    return len(present) / len(required_fields)


def tool_success_rate(trace: Dict[str, Any]) -> float:
    """
    Counts how many expected tool outputs exist in the trace.
    """
    expected_steps = [
        "skill_extraction",
        "resume_comparison",
        "resume_edits",
        "cover_letter_bullets",
        "outreach_draft",
    ]

    completed = [s for s in expected_steps if s in trace]
    return len(completed) / len(expected_steps)