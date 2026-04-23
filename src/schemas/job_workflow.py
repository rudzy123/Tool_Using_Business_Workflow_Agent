from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class JobDescriptionInput(BaseModel):
    """
    Raw job description input provided by the user.
    """
    job_title: Optional[str] = Field(
        default=None,
        description="Job title extracted or provided by the user"
    )
    company_name: Optional[str] = Field(
        default=None,
        description="Company name, if available"
    )
    job_description_text: str = Field(
        ...,
        description="Full raw job description text"
    )


class ExtractedSkill(BaseModel):
    """
    A single skill extracted from a job description.
    """
    name: str = Field(
        ...,
        description="Name of the skill (e.g., Python, Kubernetes)"
    )
    category: Optional[str] = Field(
        default=None,
        description="Optional category (e.g., language, framework, soft skill)"
    )
    importance: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relative importance of the skill (0.0–1.0)"
    )


class SkillExtractionResult(BaseModel):
    """
    Structured result of skill extraction from a job description.
    """
    extracted_skills: List[ExtractedSkill] = Field(
        ...,
        description="List of extracted skills"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence in the extraction quality"
    )
    warnings: Optional[List[str]] = Field(
        default=None,
        description="Warnings about ambiguous or low-confidence extractions"
    )


class ResumeComparisonResult(BaseModel):
    """
    Comparison between resume content and job-required skills.
    """
    matched_skills: List[str] = Field(
        ...,
        description="Skills present in both resume and job description"
    )
    missing_skills: List[str] = Field(
        ...,
        description="Skills required by the job but missing from the resume"
    )
    alignment_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall resume-to-job alignment score"
    )


class ResumeEditSuggestion(BaseModel):
    """
    Suggested resume improvement targeting a specific skill gap.
    """
    skill: str = Field(
        ...,
        description="Skill the suggestion applies to"
    )
    suggestion_text: str = Field(
        ...,
        description="Concrete suggestion to improve the resume"
    )
    priority: str = Field(
        ...,
        description="Priority level: low | medium | high"
    )


class CoverLetterBullet(BaseModel):
    """
    A single bullet point tailored for a cover letter.
    """
    bullet_text: str = Field(
        ...,
        description="Tailored bullet highlighting relevant experience"
    )
    related_skill: Optional[str] = Field(
        default=None,
        description="Primary skill demonstrated by this bullet"
    )


class OutreachDraft(BaseModel):
    """
    Draft message for recruiter or hiring manager outreach.
    """
    subject: str = Field(
        ...,
        description="Email or message subject line"
    )
    intro: str = Field(
        ...,
        description="Opening introduction paragraph"
    )
    body: str = Field(
        ...,
        description="Main outreach message content"
    )
    call_to_action: str = Field(
        ...,
        description="Closing call to action"
    )


class WorkflowRunMetadata(BaseModel):
    """
    Metadata for a single workflow execution.
    """
    run_id: str = Field(
        ...,
        description="Unique identifier for the workflow run"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when the run was executed"
    )
    status: str = Field(
        ...,
        description="Workflow status (e.g., success, failed, partial)"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Overall confidence score for the workflow output"
    )
