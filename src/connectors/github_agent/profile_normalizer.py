from typing import List, Dict, Optional
from src.core.models import CandidateProfile
from src.connectors.github_agent.models import GitHubUserProfile, GitHubRepo

class ProfileNormalizer:
    @staticmethod
    def normalize(user_profile: Dict, repo_data: List[Dict], extracted_skills_and_activity: Dict) -> Optional[CandidateProfile]:
        # Safely get values, defaulting to None if not present
        profile_obj = GitHubUserProfile(**user_profile) if user_profile else None

        if not profile_obj:
            return None

        # Assuming extracted_skills_and_activity contains:
        # "skills", "top_languages", "total_stars", "recent_activity", "oss_score"

        # Determine primary name to use
        name_to_use = profile_obj.name if profile_obj.name else profile_obj.login

        # Determine top_repo details
        top_repo_details = None
        if repo_data:
            # Sort repos by stars, then by forks
            sorted_repos = sorted(repo_data, key=lambda r: (r.get("stargazers_count", 0), r.get("forks_count", 0)), reverse=True)
            if sorted_repos:
                top_repo = sorted_repos[0]
                top_repo_details = {
                    "name": top_repo.get("name"),
                    "stars": top_repo.get("stargazers_count", 0)
                }

        return CandidateProfile(
            name=name_to_use,
            github_username=profile_obj.login,
            github_url=profile_obj.html_url, # Assuming html_url is available in profile_obj
            location=profile_obj.location,
            skills=extracted_skills_and_activity.get("skills"),
            top_languages=extracted_skills_and_activity.get("top_languages"),
            total_stars=extracted_skills_and_activity.get("total_stars"),
            recent_activity=extracted_skills_and_activity.get("recent_activity"),
            oss_score=extracted_skills_and_activity.get("oss_score"),
            top_repo=top_repo_details # Add the top_repo field
        ) 