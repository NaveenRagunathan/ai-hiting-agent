from fastapi import FastAPI, HTTPException
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the parser's FastAPI app and its models directly
from src.parser.main import app as nlp_parser_app
from src.parser.models import ParseQueryRequest # Direct import of the model

# Import the GitHub agent's FastAPI app/logic and its models
from src.connectors.github_agent.main import app as github_agent_app
from src.connectors.linkedin_agent.main import app as linkedin_agent_app

from src.core.models import ParseQueryRequest, ParseQueryResponse, SearchParams, CandidateProfile

app = FastAPI(
    title="HireAI Talent Search API",
    description="Unified API for NLP parsing and dynamic GitHub talent search.",
    version="0.1.0"
)

# Mount the NLP Parser app under /nlp
app.mount("/nlp", nlp_parser_app)

# Mount the GitHub Agent app under /github
app.mount("/github", github_agent_app)

# Mount the LinkedIn Agent app under /linkedin
app.mount("/linkedin", linkedin_agent_app, name="linkedin")

# Define a top-level endpoint that chains NLP -> GitHub
@app.post("/talent_search", response_model=List[CandidateProfile])
async def talent_search(query_request: ParseQueryRequest): # Use direct import here
    """Accepts a natural language query, parses it, and then searches GitHub for matching candidates."""
    print(f"Received natural language query: {query_request.query}")

    # 1. Use NLP Parser to get structured query
    try:
        parsed_nlp_output = await nlp_parser_app.parse_query(query_request)
        print(f"NLP Parser output: {parsed_nlp_output.dict()}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP Parsing Error: {e}")

    # 2. Convert NLP output to GitHub search params
    # Note: GitHubSearchParams expects a dict, so we convert from Pydantic model
    github_search_params = GitHubSearchParams(**parsed_nlp_output.dict())

    # 3. Use GitHub Agent to find candidates
    try:
        candidates = await github_agent_app.search_github_candidates(github_search_params)
        print(f"Found {len(candidates)} candidates from GitHub.")
        return candidates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub Search Error: {e}") 