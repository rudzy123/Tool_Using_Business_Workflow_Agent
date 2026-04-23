from typing import Dict, Any, List
from uuid import uuid4

from src.llm.mock_llm import MockLLMClient
# Later you can swap this:
# from src.llm.chat_llm import ChatLLMClient

from src.traces.recorder import TraceRecorder

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
    - Instantiate the LLM client
    - Execute tools step-by-step
    - Capture intermediate traces
    - Persist each run to disk
    - Return structured outputs
    """

    def __init__(self) -> None:
        self.run_id: str = str(uuid4())
        self.trace: Dict[str, Any] = {}

        # Choose LLM implementation (pluggable)
        self.llm = MockLLMClient()
        self.trace["llm_type"] = self.llm.__class__.__name__

        # Trace persistence
        self.recorder = TraceRecorder()

    def _serialize_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert workflow output into a JSON-serializable structure.
        """

        def serialize(value: Any):
            if hasattr(value, "model_dump"):
                return value.model_dump()
            if isinstance(value, list):
                return [serialize(v) for v in value]
            if isinstance(value, dict):
                return {k: serialize(v) for k, v in value.items()}
            return value

        return serialize(output)

    def run(
        self,
        job_description_text: str,
        resume_text: str,
        job_title: str,
        company_name: str,
    ) -> Dict[str, Any]:
        """
        Execute the full job search workflow.
        """

        if not job_description_text:
            raise ValueError("job_description_text is required")

        if not resume_text:
            raise ValueError("resume_text is required")

        # Step 1: Parse job description
        job_description: JobDescriptionInput = parse_job_description(
            raw_text=job_description_text
        )
        self.trace["job_description"] = job_description

        # Step 2: Extract required skills
        skill_result: SkillExtractionResult = extract_required_skills(
            job_description=job_description,
            llm=self.llm,
        )
        self.trace["skill_extraction"] = skill_result

        # Step 3: Load resume
        normalized_resume: str = load_resume(resume_text=resume_text)
        self.trace["resume_text"] = normalized_resume

        # Step 4: Compare resume to job
        comparison_result: ResumeComparisonResult = compare_resume_to_job(
            resume_text=normalized_resume,
            skill_result=skill_result,
        )
        self.trace["resume_comparison"] = comparison_result

        # Step 5: Suggest resume edits
        resume_edits: List[ResumeEditSuggestion] = suggest_resume_edits(
            comparison_result=comparison_result,
            llm=self.llm,
        )
        self.trace["resume_edits"] = resume_edits

        # Step 6: Generate cover letter bullets
        cover_letter_bullets: List[CoverLetterBullet] = generate_cover_letter_bullets(
            comparison_result=comparison_result,
            llm=self.llm,
        )
        self.trace["cover_letter_bullets"] = cover_letter_bullets

        # Step 7: Generate outreach draft
        outreach_draft: OutreachDraft = generate_outreach_draft(
            job_title=job_title,
            company_name=company_name,
            llm=self.llm,
        )
        self.trace["outreach_draft"] = outreach_draft

        # Metadata
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

        # ✅ Day 3: Persist run
        serialized_output = self._serialize_output(output)
        self.recorder.save_run(self.run_id, serialized_output)

        return output