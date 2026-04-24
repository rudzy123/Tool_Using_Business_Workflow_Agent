
import pytest

from src.agent.job_search_workflow import JobSearchWorkflow
from src.schemas.approval import ApprovalDecision


def test_workflow_pauses_for_resume_edit_approval():
    workflow = JobSearchWorkflow()

    result = workflow.run(
        job_description_text="Looking for a Python developer.",
        resume_text="Experienced Python engineer.",
        job_title="Python Developer",
        company_name="TestCorp",
    )

    assert result["status"] == "awaiting_approval"
    assert result["stage"] == "resume_edit_suggestions"

    # Ensure state was persisted
    persisted = workflow.repo.load(workflow.run_id)
    assert persisted is not None
    assert persisted.status == "awaiting_approval"
    assert not persisted.resume_edits_approved

def test_workflow_resumes_after_resume_edit_approval():
    workflow = JobSearchWorkflow()

    workflow.run(
        job_description_text="Looking for a Python developer.",
        resume_text="Experienced Python engineer.",
        job_title="Python Developer",
        company_name="TestCorp",
    )

    workflow.resume_edits_gate.approve(
        ApprovalDecision(
            stage="resume_edit_suggestions",
            approved=True,
            reviewer="tester",
        )
    )

    result = workflow.run(
        job_description_text="ignored",
        resume_text="ignored",
        job_title="ignored",
        company_name="ignored",
    )

    assert result["status"] == "awaiting_approval"
    assert result["stage"] == "outreach_draft"

    persisted = workflow.repo.load(workflow.run_id)
    assert persisted.resume_edits_approved is True

def test_workflow_completes_after_all_approvals():
    workflow = JobSearchWorkflow()

    workflow.run(
        job_description_text="Looking for a Python developer.",
        resume_text="Experienced Python engineer.",
        job_title="Python Developer",
        company_name="TestCorp",
    )

    workflow.resume_edits_gate.approve(
        ApprovalDecision(
            stage="resume_edit_suggestions",
            approved=True,
            reviewer="tester",
        )
    )

    workflow.run(
        job_description_text="ignored",
        resume_text="ignored",
        job_title="ignored",
        company_name="ignored",
    )

    workflow.outreach_gate.approve(
        ApprovalDecision(
            stage="outreach_draft",
            approved=True,
            reviewer="tester",
        )
    )

    result = workflow.run(
        job_description_text="ignored",
        resume_text="ignored",
        job_title="ignored",
        company_name="ignored",
    )

    assert "metadata" in result
    assert result["metadata"].status == "success"

    persisted = workflow.repo.load(workflow.run_id)
    assert persisted.status == "completed"

def test_workflow_recovery_after_restart(tmp_path):
    workflow = JobSearchWorkflow()

    workflow.run(
        job_description_text="Looking for a Python developer.",
        resume_text="Experienced Python engineer.",
        job_title="Python Developer",
        company_name="TestCorp",
    )

    workflow.resume_edits_gate.approve(
        ApprovalDecision(
            stage="resume_edit_suggestions",
            approved=True,
            reviewer="tester",
        )
    )

    workflow.run(
        job_description_text="ignored",
        resume_text="ignored",
        job_title="ignored",
        company_name="ignored",
    )

    # Simulate restart
    repo = workflow.repo
    persisted = repo.load(workflow.run_id)

    recovered = JobSearchWorkflow.from_persisted(persisted)

    assert recovered.resume_edits_gate.is_approved()
    assert not recovered.outreach_gate.is_approved()
    assert recovered._inputs is not None