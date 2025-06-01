from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict

# --- NLP Parser Models (from Day 1) ---
class ParseQueryRequest(BaseModel):
    query: str = Field(..., description="The raw user query to parse.")

class ParseQueryResponse(BaseModel):
    intent: str
    title: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    location: Optional[Union[str, List[str]]] = None
    work_type: Optional[Union[str, List[str]]] = None

# --- Universal Search Parameters (was GitHubSearchParams) ---
class SearchParams(BaseModel):
    intent: str
    title: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    location: Optional[Union[str, List[str]]] = None
    work_type: Optional[Union[str, List[str]]] = None

# --- Universal Candidate Profile (was in GitHub agent) ---
class CandidateProfile(BaseModel):
    name: Optional[str] = None
    github_username: Optional[str] = None # Make Optional as it might be from LinkedIn
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None # New field for LinkedIn profiles
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    top_languages: Optional[List[str]] = None
    total_stars: Optional[int] = None
    recent_activity: Optional[str] = None # Last active timestamp
    oss_score: Optional[int] = None # Heuristic score for OSS contributions
    top_repo: Optional[Dict] = None # Top GitHub repo details
    # Add more common fields as needed from LinkedIn/other sources 