from typing import Optional, Any
from pydantic import BaseModel


class StartWorkflowRequest(BaseModel):
    job_description_text: str
    resume_text: str
    job_title: str
    company_name: str


class WorkflowResponse(BaseModel):
    status: str
    stage: Optional[str] = None
    run_id: str
    output: Optional[Any] = None


class ApprovalRequest(BaseModel):
    stage: str
    approved: bool
    reviewer: Optional[str] = None
    comments: Optional[str] = None