from typing import List, Dict, Optional
from src.core.models import CandidateProfile
from src.connectors.linkedin_agent.models import LinkedInRawProfile

class LinkedInProfileNormalizer:
    @staticmethod
    def normalize_profile(raw_profile: LinkedInRawProfile) -> CandidateProfile:
        """
        Normalizes a raw LinkedIn profile into the universal CandidateProfile format.
        """
        # Extract skills from raw_profile. This is a simplified extraction.
        normalized_skills = []
        if raw_profile.skills:
            normalized_skills.extend(raw_profile.skills)
        
        # Extract experience details
        experience_summary = None
        if raw_profile.experience:
            experience_summary = ", ".join([f"{exp.get('title', '')} at {exp.get('company', '')}" for exp in raw_profile.experience])

        return CandidateProfile(
            name=raw_profile.name,
            linkedin_url=raw_profile.profile_url,
            location=raw_profile.location,
            skills=normalized_skills if normalized_skills else None,
            # For LinkedIn, we don't have direct GitHub fields, so they remain None
            github_username=None,
            github_url=None,
            top_languages=None,
            total_stars=None,
            recent_activity=None,
            oss_score=None,
            top_repo=None
            # You can map more LinkedIn-specific fields to generic CandidateProfile fields
            # or add LinkedIn-specific fields to CandidateProfile if they are universally useful.
        ) 