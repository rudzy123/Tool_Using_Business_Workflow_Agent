from fastapi import APIRouter, HTTPException

from src.agent.job_search_workflow import JobSearchWorkflow
from src.schemas.approval import ApprovalDecision
from src.api.models import (
    StartWorkflowRequest,
    WorkflowResponse,
    ApprovalRequest,
)

router = APIRouter()

# VERY IMPORTANT:
# For now, we keep workflows in-memory.
# This can later be replaced by Redis / DB.
WORKFLOWS: dict[str, JobSearchWorkflow] = {}
@router.post("/workflow/start", response_model=WorkflowResponse)
def start_workflow(request: StartWorkflowRequest):
    workflow = JobSearchWorkflow()
    result = workflow.run(**request.model_dump())

    WORKFLOWS[workflow.run_id] = workflow

    if result.get("status") == "awaiting_approval":
        return WorkflowResponse(
            status="awaiting_approval",
            stage=result["stage"],
            run_id=result["run_id"],
            output=result["output"],
        )

    return WorkflowResponse(
        status="completed",
        run_id=workflow.run_id,
        output=result,
    )

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

    if request.stage == "resume_edit_suggestions":
        workflow.resume_edits_gate.approve(decision)
    elif request.stage == "outreach_draft":
        workflow.outreach_gate.approve(decision)
    else:
        raise HTTPException(status_code=400, detail="Unknown approval stage")

    # Resume workflow
    result = workflow.run(
        job_description_text="",
        resume_text="",
        job_title="",
        company_name="",
    )

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