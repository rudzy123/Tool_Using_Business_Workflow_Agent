from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.api.routes import WORKFLOWS
from src.schemas.approval import ApprovalDecision

router = APIRouter()
templates = Jinja2Templates(directory="src/api/templates")


@router.get("/ui/workflow/{run_id}", response_class=HTMLResponse)
def show_approval_page(request: Request, run_id: str):
    workflow = WORKFLOWS.get(run_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Detect which gate is currently blocking
    if workflow.resume_edits_gate.requires_approval():
        stage = "resume_edit_suggestions"
        output = workflow.trace.get("resume_edits")
    elif workflow.outreach_gate.requires_approval():
        stage = "outreach_draft"
        output = workflow.trace.get("outreach_draft")
    else:
        return HTMLResponse("<h2>Workflow already completed.</h2>")

    return templates.TemplateResponse(
        "approval.html",
        {
            "request": request,
            "run_id": run_id,
            "stage": stage,
            "output": output,
        },
    )


@router.post("/ui/workflow/{run_id}")
def submit_approval(run_id: str, decision: str = Form(...)):
    workflow = WORKFLOWS.get(run_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    approved = decision == "approve"

    # Determine active gate
    if workflow.resume_edits_gate.requires_approval():
        stage = "resume_edit_suggestions"
        gate = workflow.resume_edits_gate
    elif workflow.outreach_gate.requires_approval():
        stage = "outreach_draft"
        gate = workflow.outreach_gate
    else:
        return HTMLResponse("<h2>Nothing to approve.</h2>")

    gate.approve(
        ApprovalDecision(
            stage=stage,
            approved=approved,
            reviewer="ui-user",
            comments="Approved via web UI" if approved else "Rejected via web UI",
        )
    )

    # Resume workflow
    result = workflow.run(**workflow._inputs)

    # Redirect back to approval page if another gate remains
    if result.get("status") == "awaiting_approval":
        return RedirectResponse(
            url=f"/ui/workflow/{run_id}",
            status_code=303,
        )

    return HTMLResponse("<h2>✅ Workflow completed successfully.</h2>")