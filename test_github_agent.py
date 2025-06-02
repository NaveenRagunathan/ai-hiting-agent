import asyncio
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional

# Load environment variables
load_dotenv()

# Test with the local version of the GitHub agent
import sys
sys.path.append('.')
from src.connectors.github_agent.main import search_github_candidates
from src.core.models import SearchParams

class TestSearchParams(BaseModel):
    """Test version of SearchParams with all fields optional"""
    title: Optional[str] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    work_type: Optional[str] = None
    limit: Optional[int] = 5

async def run_test(query: str):
    print(f"\n{'='*50}")
    print(f"Testing query: {query}")
    
    # Create search parameters
    params = SearchParams(
        title=query,
        skills=["python"],
        limit=5
    )
    
    try:
        # Call the search function
        result = await search_github_candidates(params)
        
        # Print results
        print(f"\nSearch successful: {result.success}")
        print(f"Message: {result.message}")
        print(f"Found {len(result.candidates)} candidates")
        
        if result.candidates:
            print("\nSample candidate:")
            sample = result.candidates[0]
            print(f"Name: {sample.get('name')}")
            print(f"Login: {sample.get('login')}")
            print(f"URL: {sample.get('html_url')}")
            print(f"Bio: {sample.get('bio', 'No bio')[:100]}...")
            print(f"Repos: {len(sample.get('repositories', []))}")
            
    except Exception as e:
        print(f"\nError during search: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status}")
            print(f"Response body: {e.response.body}")

async def main():
    test_queries = [
        "python developer",
        "machine learning engineer",
        "data scientist"
    ]
    
    for query in test_queries:
        await run_test(query)

if __name__ == "__main__":
    asyncio.run(main())
