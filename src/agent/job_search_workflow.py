from typing import Dict, Any, List
from uuid import uuid4

from app.tools.job_workflow_tools import (
    parse_job_description,
    extract_required_skills,
    load_resume,
    compare_resume_to_job,
    suggest_resume_edits,
    generate_cover_letter_bullets,
    generate_outreach_draft,
)

from app.schemas.job_workflow import (
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
    Orchestrates the job search and outreach workflow.

    This class coordinates tool execution, captures intermediate outputs,
    performs basic validation, and returns structured results.

    It intentionally avoids any UI, API, or LLM concerns.
    """

    def __init__(self) -> None:
        self.run_id: str = str(uuid4())
        self.trace: Dict[str, Any] = {}

    def run(
        self,
        job_description_text: str,
        resume_text: str,
        job_title: str,
        company_name: str,
    ) -> Dict[str, Any]:
        """
        Execute the end-to-end job search workflow.

        Args:
            job_description_text: Raw job description text
            resume_text: Raw resume text
            job_title: Job title for outreach generation
            company_name: Company name for outreach generation

        Returns:
            A dictionary containing:
            - workflow metadata
            - intermediate tool outputs
            - final artifacts
        """
        if not job_description_text:
            raise ValueError("Job description text is required")

        if not resume_text:
            raise ValueError("Resume text is required")

        # Step 1: Parse job description
        job_description: JobDescriptionInput = parse_job_description(
            raw_text=job_description_text
        )
        self.trace["job_description"] = job_description

        # Step 2: Extract required skills
        skills_result: SkillExtractionResult = extract_required_skills(
            job_description=job_description
        )
        self.trace["extracted_skills"] = skills_result

        # Step 3: Load resume
        normalized_resume: str = load_resume(resume_text=resume_text)
        self.trace["resume_text"] = normalized_resume

        # Step 4: Compare resume to job
        comparison_result: ResumeComparisonResult = compare_resume_to_job(
            resume_text=normalized_resume,
            skill_result=skills_result,
        )
        self.trace["resume_comparison"] = comparison_result

        # Step 5: Suggest resume edits
        resume_edit_suggestions: List[ResumeEditSuggestion] = suggest_resume_edits(
            comparison_result=comparison_result
        )
        self.trace["resume_edits"] = resume_edit_suggestions

        # Step 6: Generate cover letter bullets
        cover_letter_bullets: List[CoverLetterBullet] = generate_cover_letter_bullets(
            comparison_result=comparison_result
        )
        self.trace["cover_letter_bullets"] = cover_letter_bullets

        # Step 7: Generate outreach draft
        outreach_draft: OutreachDraft = generate_outreach_draft(
            job_title=job_title,
            company_name=company_name,
        )
        self.trace["outreach_draft"] = outreach_draft

        # Final metadata
        metadata = WorkflowRunMetadata(
            run_id=self.run_id,
            status="success",
            confidence_score=skills_result.confidence_score,
        )

        return {
            "metadata": metadata,
            "job_description": job_description,
            "extracted_skills": skills_result,
            "resume_comparison": comparison_result,
            "resume_edit_suggestions": resume_edit_suggestions,
            "cover_letter_bullets": cover_letter_bullets,
            "outreach_draft": outreach_draft,
        }
