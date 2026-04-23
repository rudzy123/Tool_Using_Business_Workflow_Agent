from fastapi import APIRouter, HTTPException

from src.agent.job_search_workflow import JobSearchWorkflow
from src.schemas.approval import ApprovalDecision
from src.api.models import (
    StartWorkflowRequest,
    WorkflowResponse,
    ApprovalRequest,
)

router = APIRouter()

# ---------------------------------------------------------------------
# In-memory workflow registry
# NOTE: For demos and local use only.
# Can be replaced with Redis / DB later.
# ---------------------------------------------------------------------
WORKFLOWS: dict[str, JobSearchWorkflow] = {}


# ---------------------------------------------------------------------
# Start a new workflow
# ---------------------------------------------------------------------
@router.post("/workflow/start", response_model=WorkflowResponse)
def start_workflow(request: StartWorkflowRequest):
    workflow = JobSearchWorkflow()

    result = workflow.run(**request.model_dump())

    # Register workflow for later approvals
    WORKFLOWS[workflow.run_id] = workflow

    # If workflow pauses for approval
    if result.get("status") == "awaiting_approval":
        return WorkflowResponse(
            status="awaiting_approval",
            stage=result["stage"],
            run_id=result["run_id"],
            output=result["output"],
        )

    # Workflow completed without approvals
    return WorkflowResponse(
        status="completed",
        run_id=workflow.run_id,
        output=result,
    )


# ---------------------------------------------------------------------
# Approve a workflow stage and resume execution
# ---------------------------------------------------------------------
@router.post("/workflow/{run_id}/approve", response_model=WorkflowResponse)
def approve_workflow_step(run_id: str, request: ApprovalRequest):
    workflow = WORKFLOWS.get(run_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    decision = ApprovalDecision(
        stage=request.stage,
        approved=request.approved,
        reviewer=request.reviewer,
        comments=request.comments,
    )

    # Apply approval to the correct gate
    if request.stage == "resume_edit_suggestions":
        workflow.resume_edits_gate.approve(decision)
    elif request.stage == "outreach_draft":
        workflow.outreach_gate.approve(decision)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown approval stage: {request.stage}",
        )

    # Resume workflow using stored inputs
    result = workflow.run(**workflow._inputs)

    if result.get("status") == "awaiting_approval":
        return WorkflowResponse(
            status="awaiting_approval",
            stage=result["stage"],
            run_id=run_id,
            output=result["output"],
        )

    return WorkflowResponse(
        status="completed",
        run_id=run_id,
        output=result,
    )