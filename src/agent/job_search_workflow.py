
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime

from src.llm.mock_llm import MockLLMClient

from src.persistence.repository import WorkflowRepository
from src.persistence.models import PersistedWorkflow
from src.schemas.approval import ApprovalDecision

# Later you can swap with:
# from src.llm.chat_llm import ChatLLMClient

from src.traces.recorder import TraceRecorder
from src.workflows.approval_gate import ApprovalGate

from src.tools.job_workflow_tools import (
    parse_job_description,
    extract_required_skills,
    load_resume,
    compare_resume_to_job,
    suggest_resume_edits,
    generate_cover_letter_bullets,
    generate_outreach_draft,
)

from src.schemas.job_workflow import (
    WorkflowRunMetadata,
    JobDescriptionInput,
    SkillExtractionResult,
    ResumeComparisonResult,
    ResumeEditSuggestion,
    CoverLetterBullet,
    OutreachDraft,
)


class JobSearchWorkflow:
    """
    Orchestrates the end-to-end job search and outreach workflow.

    Responsibilities:
    - Execute tools step-by-step
    - Pause at human-in-the-loop approval gates
    - Resume safely after approval
    - Capture and persist traces
    - Persist workflow state for recovery
    - Return structured outputs

    This class intentionally contains:
    - NO FastAPI logic
    - NO UI logic
    - NO direct human interaction
    """

    def __init__(self) -> None:
        self.run_id: str = str(uuid4())
        self.trace: Dict[str, Any] = {}

        # Persist initial inputs for resumable execution
        self._inputs: Optional[Dict[str, Any]] = None

        # LLM (pluggable)
        self.llm = MockLLMClient()
        self.trace["llm_type"] = self.llm.__class__.__name__

        # Trace persistence (JSON traces)
        self.recorder = TraceRecorder()

        # Durable persistence (SQLite)
        self.repo = WorkflowRepository()

        # Human-in-the-loop approval gates
        self.resume_edits_gate = ApprovalGate(stage="resume_edit_suggestions")
        self.outreach_gate = ApprovalGate(stage="outreach_draft")

    @classmethod
    def from_persisted(cls, persisted: PersistedWorkflow) -> "JobSearchWorkflow":
        """
        Rehydrate a workflow from persisted state WITHOUT re-executing steps.
        Used on application startup (Day 7).
        """
        wf = cls()

        # Restore identity and state
        wf.run_id = persisted.run_id
        wf._inputs = persisted.inputs
        wf.trace = persisted.trace

        # Restore approval gate decisions
        if persisted.resume_edits_approved:
            wf.resume_edits_gate.approve(
                ApprovalDecision(
                    stage="resume_edit_suggestions",
                    approved=True,
                    reviewer="system",
                    comments="Restored from persistence",
                )
            )

        if persisted.outreach_approved:
            wf.outreach_gate.approve(
                ApprovalDecision(
                    stage="outreach_draft",
                    approved=True,
                    reviewer="system",
                    comments="Restored from persistence",
                )
            )

        return wf
    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------

    def _serialize_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert workflow output into a JSON-serializable structure.
        """

        def serialize(value: Any):
            if hasattr(value, "model_dump"):
                return serialize(value.model_dump())
            if isinstance(value, datetime):
                return value.isoformat()
            if isinstance(value, list):
                return [serialize(v) for v in value]
            if isinstance(value, dict):
                return {k: serialize(v) for k, v in value.items()}
            return value

        return serialize(output)

    def _persist_state(self, status: str) -> None:
        """
        Persist workflow state for durability across restarts.
        """
        self.repo.save(
            PersistedWorkflow(
                run_id=self.run_id,
                status=status,
                inputs=self._inputs,
                trace=self._serialize_output(self.trace),
                resume_edits_approved=self.resume_edits_gate.is_approved(),
                outreach_approved=self.outreach_gate.is_approved(),
            )
        )

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    def run(
        self,
        job_description_text: str,
        resume_text: str,
        job_title: str,
        company_name: str,
    ) -> Dict[str, Any]:
        """
        Execute or resume the job search workflow.

        The first call stores inputs.
        Subsequent calls reuse stored inputs to allow safe resumption
        after human approval.
        """

        # Store inputs once (for resumability)
        if self._inputs is None:
            if not job_description_text:
                raise ValueError("job_description_text is required")
            if not resume_text:
                raise ValueError("resume_text is required")

            self._inputs = {
                "job_description_text": job_description_text,
                "resume_text": resume_text,
                "job_title": job_title,
                "company_name": company_name,
            }

        inputs = self._inputs

        # -----------------------------------------------------------------
        # Step 1: Parse job description
        # -----------------------------------------------------------------
        job_description: JobDescriptionInput = parse_job_description(
            raw_text=inputs["job_description_text"]
        )
        self.trace["job_description"] = job_description

        # -----------------------------------------------------------------
        # Step 2: Extract required skills
        # -----------------------------------------------------------------
        skill_result: SkillExtractionResult = extract_required_skills(
            job_description=job_description,
            llm=self.llm,
        )
        self.trace["skill_extraction"] = skill_result

        # -----------------------------------------------------------------
        # Step 3: Load resume
        # -----------------------------------------------------------------
        normalized_resume: str = load_resume(
            resume_text=inputs["resume_text"]
        )
        self.trace["resume_text"] = normalized_resume

        # -----------------------------------------------------------------
        # Step 4: Compare resume to job
        # -----------------------------------------------------------------
        comparison_result: ResumeComparisonResult = compare_resume_to_job(
            resume_text=normalized_resume,
            skill_result=skill_result,
        )
        self.trace["resume_comparison"] = comparison_result

        # -----------------------------------------------------------------
        # Step 5: Suggest resume edits (APPROVAL GATED)
        # -----------------------------------------------------------------
        resume_edits: List[ResumeEditSuggestion] = suggest_resume_edits(
            comparison_result=comparison_result,
            llm=self.llm,
        )
        self.trace["resume_edits"] = resume_edits

        if self.resume_edits_gate.requires_approval():
            self._persist_state("awaiting_approval")
            return {
                "status": "awaiting_approval",
                "stage": "resume_edit_suggestions",
                "run_id": self.run_id,
                "output": resume_edits,
            }

        # -----------------------------------------------------------------
        # Step 6: Generate cover letter bullets
        # -----------------------------------------------------------------
        cover_letter_bullets: List[CoverLetterBullet] = generate_cover_letter_bullets(
            comparison_result=comparison_result,
            llm=self.llm,
        )
        self.trace["cover_letter_bullets"] = cover_letter_bullets

        # -----------------------------------------------------------------
        # Step 7: Generate outreach draft (APPROVAL GATED)
        # -----------------------------------------------------------------
        outreach_draft: OutreachDraft = generate_outreach_draft(
            job_title=inputs["job_title"],
            company_name=inputs["company_name"],
            llm=self.llm,
        )
        self.trace["outreach_draft"] = outreach_draft

        if self.outreach_gate.requires_approval():
            self._persist_state("awaiting_approval")
            return {
                "status": "awaiting_approval",
                "stage": "outreach_draft",
                "run_id": self.run_id,
                "output": outreach_draft,
            }

        # -----------------------------------------------------------------
        # Finalize
        # -----------------------------------------------------------------
        metadata = WorkflowRunMetadata(
            run_id=self.run_id,
            status="success",
            confidence_score=skill_result.confidence_score,
        )

        output = {
            "metadata": metadata,
            "job_description": job_description,
            "extracted_skills": skill_result,
            "resume_comparison": comparison_result,
            "resume_edit_suggestions": resume_edits,
            "cover_letter_bullets": cover_letter_bullets,
            "outreach_draft": outreach_draft,
            "trace": self.trace,
        }

        # Persist trace artifact (JSON)
        serialized_output = self._serialize_output(output)
        self.recorder.save_run(self.run_id, serialized_output)

        # Persist durable state (SQLite)
        self._persist_state("completed")

        return output
