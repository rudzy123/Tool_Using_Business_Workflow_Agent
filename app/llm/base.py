import abc
from typing import List, Dict, Any


class LLMClient(abc.ABC):
    """
    Abstract base class for LLM clients used in workflow agents.

    This interface exists to decouple workflows from any specific LLM implementation,
    allowing for mock, local, or hosted LLM implementations to be used interchangeably.
    """

    @abc.abstractmethod
    def extract_required_skills(self, job_description_text: str) -> List[str]:
        """
        Extract the required skills from a job description text.

        Args:
            job_description_text: The full text of the job description.

        Returns:
            A list of required skills as strings.
        """
        pass

    @abc.abstractmethod
    def generate_resume_edit_suggestions(self, missing_skills: List[str]) -> List[str]:
        """
        Generate suggestions for editing a resume based on missing skills.

        Args:
            missing_skills: List of skills that are missing from the resume.

        Returns:
            A list of suggestions for resume edits.
        """
        pass

    @abc.abstractmethod
    def generate_cover_letter_bullets(self, matched_skills: List[str]) -> List[str]:
        """
        Generate bullet points for a cover letter based on matched skills.

        Args:
            matched_skills: List of skills that match between resume and job.

        Returns:
            A list of bullet points for the cover letter.
        """
        pass

    @abc.abstractmethod
    def generate_outreach_draft(self, job_title: str, company_name: str) -> str:
        """
        Generate a draft outreach message for a job application.

        Args:
            job_title: The title of the job position.
            company_name: The name of the company.

        Returns:
            A string containing the draft outreach message.
        """
        pass