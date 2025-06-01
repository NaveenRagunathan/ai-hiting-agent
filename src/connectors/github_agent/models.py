from pydantic import BaseModel
from typing import List, Optional, Dict

# --- GitHub Agent Specific Models (Day 2) ---

class GitHubSearchUserResult(BaseModel):
    login: str
    html_url: str
    # Add other fields as needed from /search/users

class GitHubRepoSearchResult(BaseModel):
    name: str
    html_url: str
    language: Optional[str] = None
    stargazers_count: Optional[int] = None
    forks_count: Optional[int] = None
    topics: Optional[List[str]] = None
    description: Optional[str] = None
    updated_at: Optional[str] = None
    owner: Dict # This will contain 'login' for the user

class GitHubUserProfile(BaseModel):
    login: str
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    blog: Optional[str] = None
    twitter_username: Optional[str] = None
    hireable: Optional[bool] = None
    public_repos: Optional[int] = None
    followers: Optional[int] = None
    # Add other fields from /users/{username}

class GitHubRepo(BaseModel):
    name: str
    html_url: str
    language: Optional[str] = None
    stargazers_count: Optional[int] = None
    forks_count: Optional[int] = None
    topics: Optional[List[str]] = None
    description: Optional[str] = None
    updated_at: Optional[str] = None # ISO 8601 format
    # Add other fields from /users/{username}/repos 