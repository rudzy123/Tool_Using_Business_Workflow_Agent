"""
Mock LLM implementation for deterministic workflow testing and development.

This module provides a mock LLMClient that returns hard-coded, predictable outputs.
It is used for:
- Local development without external LLM calls
- Workflow testing
- CI/CD pipelines
- Deterministic evaluation baselines

WARNING:
This is a mock implementation.
Do NOT use in production.
"""

from typing import List, Dict, Any

from src.llm.base import LLMClient


class MockLLMClient(LLMClient):
    """
    Mock implementation of LLMClient.

    All methods return deterministic, schema-compatible outputs
    that exactly match what workflow tools expect.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        if self.verbose:
            print("WARNING: MockLLMClient in use. Outputs are deterministic.")

    def extract_required_skills(self, job_description_text: str) -> Dict[str, Any]:
        """
        Return mock extracted skills with confidence and warnings.

        Contract:
        {
            "skills": [
                {"name": str, "category": str, "importance": float}
            ],
            "confidence": float,
            "warnings": list[str] | None
        }
        """
        if self.verbose:
            print("MockLLMClient.extract_required_skills called")

        return {
            "skills": [
                {
                    "name": "Python",
                    "category": "language",
                    "importance": 0.9,
                },
                {
                    "name": "REST APIs",
                    "category": "framework",
                    "importance": 0.75,
                },
                {
                    "name": "Communication",
                    "category": "soft_skill",
                    "importance": 0.6,
                },
            ],
            "confidence": 0.75,
            "warnings": ["Mock LLM output"],
        }

    def generate_resume_edit_suggestions(
        self, missing_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Return mock resume edit suggestions.

        Contract:
        [
            {
                "skill": str,
                "suggestion_text": str,
                "priority": str
            }
        ]
        """
        if self.verbose:
            print("MockLLMClient.generate_resume_edit_suggestions called")

        return [
            {
                "skill": skill,
                "suggestion_text": f"Add experience or projects demonstrating {skill}.",
                "priority": "high",
            }
            for skill in missing_skills
        ]

    def generate_cover_letter_bullets(
        self, matched_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Return mock cover letter bullets.

        Contract:
        [
            {
                "bullet_text": str,
                "related_skill": str | None
            }
        ]
        """
        if self.verbose:
            print("MockLLMClient.generate_cover_letter_bullets called")

        return [
            {
                "bullet_text": f"Demonstrated hands-on experience with {skill}.",
                "related_skill": skill,
            }
            for skill in matched_skills
        ]

    def generate_outreach_draft(
        self, job_title: str, company_name: str
    ) -> Dict[str, str]:
        """
        Return a structured outreach draft.

        Contract:
        {
            "subject": str,
            "intro": str,
            "body": str,
            "call_to_action": str
        }
        """
        if self.verbose:
            print("MockLLMClient.generate_outreach_draft called")

        return {
            "subject": f"Interest in {job_title} Opportunity",
            "intro": "Hello, I hope you are doing well.",
            "body": (
                f"I recently came across the {job_title} role at {company_name} "
                "and wanted to express my interest. "
                "My background aligns well with the role, and I would value the chance "
                "to discuss how I could contribute to your team."
            ),
            "call_to_action": "I would welcome the opportunity to connect and learn more.",
        }
