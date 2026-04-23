"""
Mock LLM implementation for deterministic workflow testing and development.

This module provides a mock LLMClient that returns hard-coded, predictable outputs.
It is useful for:
- Unit testing workflows without external LLM calls
- Development and iteration on workflow logic
- CI/CD pipelines where external API calls are undesirable
- Deterministic test fixtures

WARNING: This is a mock implementation. Do not use in production.
Replace with real LLM calls before deploying to users.
"""

from typing import List

from llm.base import LLMClient


class MockLLMClient(LLMClient):
    """
    Mock implementation of LLMClient for testing and development.
    
    Returns hard-coded, deterministic outputs for all methods.
    Includes explicit warnings and TODOs indicating this is a placeholder.
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the MockLLMClient.
        
        Args:
            verbose: If True, print warnings when methods are called.
        """
        self.verbose = verbose
        if self.verbose:
            print("WARNING: Using MockLLMClient. This is a test/development implementation.")

    def extract_required_skills(self, job_description_text: str) -> List[str]:
        """
        Return mock required skills extracted from job description.
        
        For any input, returns a fixed set of skills.
        
        Args:
            job_description_text: The full text of the job description (ignored in mock).
            
        Returns:
            A deterministic list of technical and soft skills.
            
        TODO: Replace with real LLM-based skill extraction.
        TODO: Add confidence scores per skill.
        TODO: Implement parsing of actual job description content.
        """
        if self.verbose:
            print(f"MockLLMClient.extract_required_skills called (input length: {len(job_description_text)})")
        
        # Hard-coded deterministic output
        return [
            "Python",
            "JavaScript",
            "React",
            "PostgreSQL",
            "AWS",
            "Docker",
            "Communication",
            "Problem Solving",
            "Git",
            "REST APIs",
        ]

    def generate_resume_edit_suggestions(self, missing_skills: List[str]) -> List[str]:
        """
        Return mock resume edit suggestions based on missing skills.
        
        Returns generic suggestions that could apply to any set of missing skills.
        
        Args:
            missing_skills: List of skills missing from the resume (used for context only).
            
        Returns:
            A deterministic list of resume improvement suggestions.
            
        TODO: Replace with LLM-generated suggestions tailored to specific skills.
        TODO: Prioritize suggestions by impact on hiring decision.
        TODO: Include concrete action steps and examples.
        TODO: Adapt suggestions based on candidate's background/experience level.
        """
        if self.verbose:
            print(f"MockLLMClient.generate_resume_edit_suggestions called with {len(missing_skills)} skills")
        
        # Hard-coded deterministic output
        suggestions = [
            "Add a 'Projects' section showcasing hands-on experience with the missing skill.",
            "Create a GitHub profile with public repositories demonstrating proficiency.",
            "Highlight any coursework, certifications, or online training completed.",
            "Include specific metrics and achievements in role descriptions.",
            "Mention collaborations and team contributions for soft skills.",
        ]
        
        # TODO: If needed, truncate or expand suggestions based on missing_skills count
        return suggestions

    def generate_cover_letter_bullets(self, matched_skills: List[str]) -> List[str]:
        """
        Return mock cover letter bullet points for matched skills.
        
        Returns generic, high-impact bullets suitable for most roles.
        
        Args:
            matched_skills: List of skills matching between resume and job (used for context).
            
        Returns:
            A deterministic list of cover letter bullet points.
            
        TODO: Replace with LLM-generated bullets tailored to specific matched skills.
        TODO: Customize tone based on company and role type.
        TODO: Reference actual resume accomplishments for authenticity.
        TODO: Generate multiple variations for A/B testing.
        """
        if self.verbose:
            print(f"MockLLMClient.generate_cover_letter_bullets called with {len(matched_skills)} skills")
        
        # Hard-coded deterministic output
        bullets = [
            "Delivered production systems serving millions of users with a focus on reliability and performance.",
            "Led cross-functional teams through complex technical challenges, driving clear communication and collaboration.",
            "Implemented scalable infrastructure solutions that reduced deployment time by 60% and improved system uptime.",
            "Authored comprehensive documentation and mentored junior engineers, fostering a culture of knowledge sharing.",
            "Acted as a technical leader in architecting solutions that reduced operational costs while improving system resilience.",
        ]
        
        # TODO: Consider matching bullets to specific skills from matched_skills list
        return bullets

    def generate_outreach_draft(self, job_title: str, company_name: str) -> str:
        """
        Return a mock outreach draft email.
        
        Generates a generic but professional outreach template.
        
        Args:
            job_title: The title of the job position (used in template).
            company_name: The name of the company (used in template).
            
        Returns:
            A deterministic draft outreach message.
            
        TODO: Replace with LLM-generated personalized outreach.
        TODO: Add support for "warm" vs "cold" outreach variations.
        TODO: Include dynamic placeholders for candidate customization.
        TODO: Generate subject lines optimized for open rates.
        TODO: Add A/B testing variations.
        """
        if self.verbose:
            print(f"MockLLMClient.generate_outreach_draft called for {job_title} at {company_name}")
        
        # Hard-coded deterministic template with interpolated job_title and company_name
        draft = f"""Subject: Excited about the {job_title} opportunity at {company_name}

Dear Hiring Manager,

I hope this message finds you well. I recently came across the {job_title} position at {company_name} and was impressed by your team's work on innovative solutions in this space.

With my background in building scalable systems and leading technical initiatives, I believe I could contribute meaningfully to your team. I'm particularly drawn to {company_name}'s commitment to [company mission/values], and I'd welcome the opportunity to discuss how my experience aligns with your needs.

I've attached my resume and would be delighted to connect at your convenience.

Best regards,
[Your Name]
[Your Phone]
[Your Email]
[LinkedIn Profile]"""
        
        # TODO: Parse this into structured fields (subject, intro, body, call_to_action)
        # TODO: Make the template more dynamic based on company_name and job_title
        return draft.strip()
