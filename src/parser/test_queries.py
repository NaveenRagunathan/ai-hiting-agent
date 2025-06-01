import sys
import os
import json
import requests

# Add the project root (ai-hiring-copilot) to sys.path for module discovery
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.parser.parsing_agent.llm_parser import LLMParserAgent
from src.parser.parsing_agent.groq_client import OpenRouterClient
from src.parser.parsing_agent.validator import Validator
from dotenv import load_dotenv

# Import the GitHub search function
from src.connectors.github_agent.cli import run_github_search
from src.core.models import SearchParams

load_dotenv()

sample_queries = [
    "Find senior Gen-AI engineers with LangChain + RAG experience in Europe, open to contract work",
    "Python developerS"
]

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
llm_agent = LLMParserAgent(OpenRouterClient(api_key=openrouter_api_key))

if not openrouter_api_key:
    print("Error: OPENROUTER_API_KEY environment variable not set.")
    print("Please create a .env file in the project root with: OPENROUTER_API_KEY=YOUR_KEY_HERE")
    sys.exit(1)

print("\n--- Running NLP Parser and GitHub Search Tests ---")

for query in sample_queries:
    print(f"\nInput Query: {query}")
    try:
        # Phase 1: NLP Parsing
        parsed = llm_agent.parse(query)
        validated = Validator.validate(parsed)
        print(f"NLP Parsed Output: {json.dumps(validated, indent=2)}")

        # Phase 2: GitHub Talent Search
        print("\nInitiating GitHub search based on NLP output...")
        candidates = run_github_search(validated)

        print("\n--- GitHub Search Results ---")
        if candidates:
            for i, candidate in enumerate(candidates):
                print(f"Candidate {i+1}:")
                print(json.dumps(candidate.dict(), indent=2))
        else:
            print("No candidates found matching the criteria from GitHub.")
        print("-----------------------------")

    except Exception as e:
        print(f"Error processing query or GitHub search: {e}")
        print("-----------------------------")

print("\n--- Running LinkedIn Agent Test ---")

linkedin_test_params = {
    "intent": "find_candidates",
    "title": "Software Engineer",
    "skills": ["Python", "FastAPI"],
    "location": "San Francisco",
    "experience_level": "senior",
    "work_type": "full-time"
}

try:
    print(f"\nSending test query to LinkedIn Agent: {json.dumps(linkedin_test_params, indent=2)}")
    # Assuming the main FastAPI app is running on http://127.0.0.1:8000
    # You might need to adjust the URL if running in a different environment
    response = requests.post("http://127.0.0.1:8000/linkedin/search", json=linkedin_test_params)
    response.raise_for_status() # Raise an exception for HTTP errors

    linkedin_candidates = response.json()

    print("\n--- LinkedIn Search Results ---")
    if linkedin_candidates:
        for i, candidate_data in enumerate(linkedin_candidates):
            candidate = CandidateProfile(**candidate_data) # Convert dict to Pydantic model
            print(f"Candidate {i+1}:")
            print(json.dumps(candidate.dict(), indent=2))
    else:
        print("No candidates found matching the criteria from LinkedIn.")
    print("-----------------------------")

except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the FastAPI application. Please ensure main_app.py is running (e.g., uvicorn main_app:app --reload).")
except Exception as e:
    print(f"Error processing LinkedIn search: {e}")
    print("-----------------------------") 