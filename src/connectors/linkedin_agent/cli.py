import sys
import os
import json
from typing import List

# Add the project root to sys.path for module discovery
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.core.models import SearchParams, CandidateProfile
from src.connectors.linkedin_agent.search_query_generator import LinkedInSearchQueryGenerator
from src.connectors.linkedin_agent.linkedin_fetcher import LinkedInFetcher
from src.connectors.linkedin_agent.profile_normalizer import LinkedInProfileNormalizer
from src.connectors.linkedin_agent.models import LinkedInRawProfile

def run_linkedin_search(nlp_output: dict) -> List[CandidateProfile]:
    try:
        # 1. Generate LinkedIn search query
        params = SearchParams(**nlp_output)
        linkedin_query = LinkedInSearchQueryGenerator.generate_linkedin_search_query(params)
        print(f"\nGenerated LinkedIn search query: {linkedin_query}")

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
            print("No LinkedIn candidates found matching the criteria.")

        print(f"Returning {len(candidate_profiles)} filtered candidates.")
        return candidate_profiles

    except Exception as e:
        print(f"Error during LinkedIn search: {e}")
        return []

if __name__ == "__main__":
    # Simulate NLP Parser output
    sample_nlp_output = {
      "intent": "find_candidates",
      "title": "Data Scientist",
      "skills": ["Machine Learning", "Python"],
      "location": "New York",
      "experience_level": "mid-level",
      "work_type": "full-time"
    }

    print("--- Starting LinkedIn Talent Search CLI Test ---")
    print(f"Input NLP Output: {json.dumps(sample_nlp_output, indent=2)}")
    
    candidates = run_linkedin_search(sample_nlp_output)

    print("\n--- Found Candidates ---")
    if candidates:
        for i, candidate in enumerate(candidates):
            print(f"Candidate {i+1}:")
            print(json.dumps(candidate.dict(), indent=2))
    else:
        print("No candidates found matching the criteria.")
    print("------------------------") 