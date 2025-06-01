import sys
import os
import json
from typing import List, Set

# Add the project root to sys.path for module discovery
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.core.models import SearchParams, CandidateProfile
from src.connectors.github_agent.models import GitHubSearchUserResult, GitHubRepoSearchResult
from src.connectors.github_agent.search_query_generator import SearchQueryGenerator
from src.connectors.github_agent.github_fetcher import GitHubFetcher
from src.connectors.github_agent.profile_collector import ProfileCollector
from src.connectors.github_agent.skill_activity_filter import SkillActivityFilter
from src.connectors.github_agent.profile_normalizer import ProfileNormalizer
from dotenv import load_dotenv

load_dotenv()

def run_github_search(nlp_output: dict) -> List[CandidateProfile]:
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set. Please set it in your .env file.")
        return []

    github_fetcher = GitHubFetcher(github_token=github_token)
    profile_collector = ProfileCollector(github_fetcher=github_fetcher)

    try:
        # 1. Generate GitHub REPOSITORY search query
        params = SearchParams(**nlp_output)
        github_repo_query = SearchQueryGenerator.generate_github_repo_search_query(params.dict())
        print(f"\nGenerated GitHub REPO search query: {github_repo_query}")

        # 2. Search GitHub repositories and extract unique user logins
        repo_search_results_raw = github_fetcher.search_repositories(github_repo_query)
        if not repo_search_results_raw or not repo_search_results_raw.get("items"):
            print("No initial GitHub repositories found for the given query.")
            return []
        
        unique_github_logins: Set[str] = set()
        for item in repo_search_results_raw["items"]:
            repo_result = GitHubRepoSearchResult(**item)
            if repo_result.owner and repo_result.owner.get("login"):
                unique_github_logins.add(repo_result.owner["login"])
        
        print(f"Found {len(unique_github_logins)} unique GitHub users from repository search.")

        # Convert unique logins to GitHubSearchUserResult for profile_collector
        users_to_collect = [GitHubSearchUserResult(login=login, html_url=f"https://github.com/{login}") 
                            for login in list(unique_github_logins)]

        # 3. Collect detailed profiles and repos for these unique users
        collected_raw_profiles = profile_collector.collect_profiles(users_to_collect)
        print(f"Collected detailed data for {len(collected_raw_profiles)} profiles.")

        # 4. Filter and Normalize profiles
        final_candidates: List[CandidateProfile] = []
        for raw_profile_data in collected_raw_profiles:
            user_profile = raw_profile_data.get("user_profile", {})
            user_repos = raw_profile_data.get("user_repos", [])

            # Extract skills and analyze activity
            extracted_skills = SkillActivityFilter.extract_skills(user_profile, user_repos)
            activity_metrics = SkillActivityFilter.analyze_activity(user_profile, user_repos)
            
            # Combine all extracted and analyzed data
            combined_data = {
                **user_profile, 
                "skills": extracted_skills, 
                "top_languages": activity_metrics.get("top_languages"),
                "total_stars": activity_metrics.get("total_stars"),
                "recent_activity": activity_metrics.get("recent_activity"),
                "oss_score": activity_metrics.get("oss_score"),
            }
            
            # Normalize into CandidateProfile
            candidate = ProfileNormalizer.normalize(user_profile, user_repos, combined_data)
            
            if candidate and SkillActivityFilter.apply_filters(candidate.dict()):
                final_candidates.append(candidate)
            else:
                print(f"Skipping candidate: {candidate.github_username if candidate else 'Unknown'} (failed filter)")

        print(f"Returning {len(final_candidates)} filtered candidates.")
        return final_candidates

    except Exception as e:
        print(f"Error during GitHub search: {e}")
        return []

if __name__ == "__main__":
    # Simulate NLP Parser output
    sample_nlp_output = {
      "intent": "find",
      "title": "Gen-AI Engineer",
      "skills": ["LangChain", "RAG"],
      "experience_level": "senior",
      "location": "Europe",
      "work_type": "contract"
    }

    print("--- Starting GitHub Talent Search CLI Test ---")
    print(f"Input NLP Output: {json.dumps(sample_nlp_output, indent=2)}")
    
    candidates = run_github_search(sample_nlp_output)

    print("\n--- Found Candidates ---")
    if candidates:
        for i, candidate in enumerate(candidates):
            print(f"Candidate {i+1}:")
            print(json.dumps(candidate.dict(), indent=2))
    else:
        print("No candidates found matching the criteria.")
    print("------------------------") 