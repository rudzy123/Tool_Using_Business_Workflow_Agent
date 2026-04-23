from typing import Optional
from src.schemas.approval import ApprovalDecision


class ApprovalGate:
    """
    Represents a blocking approval gate in a workflow.
    """

    def __init__(self, stage: str):
        self.stage = stage
        self.decision: Optional[ApprovalDecision] = None

    def requires_approval(self) -> bool:
        return self.decision is None

    def approve(self, decision: ApprovalDecision) -> None:
        if decision.stage != self.stage:
            raise ValueError("Approval decision stage mismatch")
        self.decision = decision

    def is_approved(self) -> bool:
        return self.decision is not None and self.decision.approved is True