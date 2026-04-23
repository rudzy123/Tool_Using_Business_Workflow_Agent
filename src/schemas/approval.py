from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class ApprovalDecision(BaseModel):
    """
    Represents a human-in-the-loop approval decision.
    """
    stage: str = Field(
        ...,
        description="Workflow stage being approved (e.g., outreach_draft)"
    )
    approved: bool = Field(
        ...,
        description="Whether the output was approved"
    )
    reviewer: Optional[str] = Field(
        default=None,
        description="Identifier for the human reviewer"
    )
    comments: Optional[str] = Field(
        default=None,
        description="Optional reviewer feedback"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the approval decision"
    )