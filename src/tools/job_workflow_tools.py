from typing import List

from app.llm.base import LLMClient
from app.schemas.job_workflow import (
    JobDescriptionInput,
    SkillExtractionResult,
    ExtractedSkill,
    ResumeComparisonResult,
    ResumeEditSuggestion,
    CoverLetterBullet,
    OutreachDraft,
)


def parse_job_description(
    raw_text: str,
) -> JobDescriptionInput:
    """
    Parse raw job description text into a structured JobDescriptionInput.
    """
    return JobDescriptionInput(
        job_description_text=raw_text
    )


def extract_required_skills(
    job_description: JobDescriptionInput,
    llm: LLMClient,
) -> SkillExtractionResult:
    """
    Extract required skills from a structured job description
    using an injected LLM client.
    """
    raw_result = llm.extract_required_skills(
        job_description.job_description_text
    )

    return SkillExtractionResult(
        extracted_skills=[
            ExtractedSkill(**skill) for skill in raw_result["skills"]
        ],
        confidence_score=raw_result.get("confidence", 0.0),
        warnings=raw_result.get("warnings"),
    )


def load_resume(
    resume_text: str,
) -> str:
    """
    Load and normalize resume content.
    """
    return resume_text.strip()


def compare_resume_to_job(
    resume_text: str,
    skill_result: SkillExtractionResult,
) -> ResumeComparisonResult:
    """
    Compare resume content against extracted job skills.
    """
    matched_skills: List[str] = []
    missing_skills: List[str] = []

    resume_lower = resume_text.lower()

    for skill in skill_result.extracted_skills:
        if skill.name.lower() in resume_lower:
            matched_skills.append(skill.name)
        else:
            missing_skills.append(skill.name)

    alignment_score = (
        len(matched_skills) / max(len(skill_result.extracted_skills), 1)
    )

    return ResumeComparisonResult(
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        alignment_score=alignment_score,
    )


def suggest_resume_edits(
    comparison_result: ResumeComparisonResult,
    llm: LLMClient,
) -> List[ResumeEditSuggestion]:
    """
    Generate resume edit suggestions using an injected LLM client.
    """
    raw_suggestions = llm.generate_resume_edit_suggestions(
        comparison_result.missing_skills
    )

    return [
        ResumeEditSuggestion(**suggestion)
        for suggestion in raw_suggestions
    ]


def generate_cover_letter_bullets(
    comparison_result: ResumeComparisonResult,
    llm: LLMClient,
) -> List[CoverLetterBullet]:
    """
    Generate tailored cover letter bullets using an injected LLM client.
    """
    raw_bullets = llm.generate_cover_letter_bullets(
        comparison_result.matched_skills
    )

    return [
        CoverLetterBullet(**bullet)
        for bullet in raw_bullets
    ]


def generate_outreach_draft(
    job_title: str,
    company_name: str,
    llm: LLMClient,
) -> OutreachDraft:
    """
    Generate a recruiter or hiring manager outreach draft
    using an injected LLM client.
    """
    raw_draft = llm.generate_outreach_draft(
        job_title=job_title,
        company_name=company_name,
    )

    return OutreachDraft(**raw_draft)