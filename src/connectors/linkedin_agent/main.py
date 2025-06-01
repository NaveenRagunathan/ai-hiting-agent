from fastapi import FastAPI, HTTPException
from typing import List
from src.core.models import SearchParams, CandidateProfile
from src.connectors.linkedin_agent.search_query_generator import LinkedInSearchQueryGenerator
from src.connectors.linkedin_agent.linkedin_fetcher import LinkedInFetcher
from src.connectors.linkedin_agent.profile_normalizer import LinkedInProfileNormalizer
from src.connectors.linkedin_agent.models import LinkedInRawProfile

app = FastAPI(
    title="LinkedIn Agent",
    description="Agent for generating LinkedIn search queries, fetching profiles, and normalizing data.",
    version="0.1.0",
)

@app.post("/search", response_model=List[CandidateProfile])
async def search_linkedin_profiles(params: SearchParams):
    """
    Searches for LinkedIn profiles based on the provided search parameters,
    fetches details, and normalizes them into a universal CandidateProfile format.
    """
    try:
        # 1. Generate LinkedIn search query
        linkedin_query = LinkedInSearchQueryGenerator.generate_linkedin_search_query(params)
        print(f"Generated LinkedIn search query: {linkedin_query}")

        # 2. Search for profiles using the LinkedIn Fetcher (simulated)
        fetcher = LinkedInFetcher()
        raw_profile_results = fetcher.search_profiles(linkedin_query)
        print(f"Found {len(raw_profile_results)} raw LinkedIn profiles.")

        candidate_profiles: List[CandidateProfile] = []
        for raw_profile_summary in raw_profile_results:
            # 3. Fetch detailed profile (simulated)
            detailed_raw_profile = fetcher.get_profile_details(raw_profile_summary.get("profile_url"))
            
            if detailed_raw_profile:
                # 4. Normalize the raw profile into CandidateProfile
                linkedin_raw_profile_model = LinkedInRawProfile(**detailed_raw_profile)
                normalized_profile = LinkedInProfileNormalizer.normalize_profile(linkedin_raw_profile_model)
                candidate_profiles.append(normalized_profile)
        
        if not candidate_profiles:
            raise HTTPException(status_code=404, detail="No LinkedIn candidates found matching the criteria.")

        return candidate_profiles

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during LinkedIn profile search: {str(e)}") 