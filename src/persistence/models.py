#DB schema (pure data)
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class PersistedWorkflow:
    run_id: str
    status: str
    inputs: Dict[str, Any]
    trace: Dict[str, Any]
    resume_edits_approved: bool
    outreach_approved: bool