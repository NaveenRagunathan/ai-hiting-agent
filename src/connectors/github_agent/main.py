import logging
import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel

from src.core.models import SearchParams, CandidateProfile
from src.connectors.github_agent.models import GitHubSearchUserResult, GitHubRepoSearchResult
from src.connectors.github_agent.search_query_generator import SearchQueryGenerator
from src.connectors.github_agent.github_fetcher import GitHubFetcher, RateLimitExceeded
from src.connectors.github_agent.profile_collector import ProfileCollector
from src.connectors.github_agent.skill_activity_filter import SkillActivityFilter
from src.connectors.github_agent.profile_normalizer import ProfileNormalizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="GitHub Talent Search API",
    description="API for searching and analyzing GitHub profiles for talent discovery",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_github_fetcher():
    """Dependency for GitHubFetcher with error handling for missing token."""
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        logger.warning(
            "GITHUB_TOKEN environment variable not set. "
            "GitHub API rate limits will be severely restricted (60 requests/hour)."
        )
    return GitHubFetcher(github_token=github_token)

# Initialize components
profile_collector = ProfileCollector(github_fetcher=get_github_fetcher())
skill_activity_filter = SkillActivityFilter()
profile_normalizer = ProfileNormalizer()

class SearchResponse(BaseModel):
    """Response model for search results."""
    success: bool
    message: str
    candidates: List[Dict[str, Any]] = []
    search_metadata: Dict[str, Any] = {}
    error: Optional[str] = None

@app.post("/search", response_model=SearchResponse)
async def search_github_candidates(
    params: SearchParams,
    fetcher: GitHubFetcher = Depends(get_github_fetcher)
) -> SearchResponse:
    """
    Search for GitHub candidates based on search parameters.
    
    This endpoint performs a repository search based on the provided parameters,
    then collects and analyzes profiles of repository owners.
    """
    try:
        logger.info(f"Starting search with params: {params.dict()}")
        
        # 1. Generate GitHub repository search query
        try:
            github_repo_query = SearchQueryGenerator.generate_github_repo_search_query(params.dict())
            logger.info(f"Generated GitHub search query: {github_repo_query}")
        except Exception as e:
            logger.error(f"Error generating search query: {e}")
            return SearchResponse(
                success=False,
                message="Failed to generate search query",
                error=str(e)
            )

        # 2. Search GitHub repositories
        try:
            logger.info(f"Searching GitHub repositories with query: {github_repo_query}")
            repo_search_results = fetcher.search_repositories(
                query=github_repo_query,
                per_page=min(30, params.limit or 30),  # Default to 30 results max
                max_pages=2  # Limit to 2 pages to avoid excessive API calls
            )
            
            if not repo_search_results or not repo_search_results.get('items'):
                logger.info("No repositories found matching the search criteria")
                return SearchResponse(
                    success=True,
                    message="No repositories found matching the search criteria",
                    candidates=[],
                    search_metadata={"total_count": 0}
                )
                
            logger.info(f"Found {len(repo_search_results['items'])} repositories")
            
            # 3. Extract unique users from repository results
            unique_users = {}
            for item in repo_search_results['items']:
                try:
                    repo = GitHubRepoSearchResult(**item)
                    if repo.owner and repo.owner.login and repo.owner.login not in unique_users:
                        unique_users[repo.owner.login] = repo.owner
                except Exception as e:
                    logger.warning(f"Error processing repository result {item.get('id')}: {e}")
            
            if not unique_users:
                return SearchResponse(
                    success=True,
                    message="No valid users found in repository results",
                    candidates=[],
                    search_metadata={"total_count": 0}
                )
                
            logger.info(f"Found {len(unique_users)} unique users to analyze")
            
            # 4. Collect detailed profiles
            users_to_collect = [
                GitHubSearchUserResult(login=login, html_url=f"https://github.com/{login}")
                for login in unique_users.keys()
            ]
            
            profiles = await profile_collector.collect_profiles(users_to_collect)
            
            # 5. Filter and normalize profiles
            filtered_profiles = []
            for profile in profiles:
                try:
                    normalized = profile_normalizer.normalize(profile)
                    if skill_activity_filter.matches_criteria(normalized, params):
                        filtered_profiles.append(normalized)
                except Exception as e:
                    logger.warning(f"Error processing profile {profile.get('login')}: {e}")
            
            logger.info(f"Successfully processed {len(filtered_profiles)} profiles")
            
            return SearchResponse(
                success=True,
                message=f"Found {len(filtered_profiles)} matching candidates",
                candidates=[p.dict() for p in filtered_profiles],
                search_metadata={
                    "total_count": len(filtered_profiles),
                    "query": github_repo_query,
                    "repositories_searched": len(repo_search_results['items']),
                    "unique_users_found": len(unique_users)
                }
            )
            
        except RateLimitExceeded as e:
            logger.error(f"GitHub API rate limit exceeded: {e}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="GitHub API rate limit exceeded. Please try again later or provide a GitHub token for higher limits."
            )
        except Exception as e:
            logger.error(f"Error during GitHub search: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during GitHub search: {str(e)}"
            )
            
    except Exception as e:
        logger.error(f"Unexpected error in search_github_candidates: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
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
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}") 