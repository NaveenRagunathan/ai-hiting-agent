import os
import requests
from typing import Dict, List, Optional

class GitHubFetcher:
    BASE_URL = "https://api.github.com"

    def __init__(self, github_token: Optional[str] = None):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if github_token:
            self.headers["Authorization"] = f"Bearer {github_token}"
        else:
            print("WARNING: GitHub token is missing. API requests will be unauthenticated and subject to severe rate limits.")

    def _make_request(self, method: str, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        print(f"DEBUG: Making {method} request to {url} with params: {params}")
        try:
            response = requests.request(method, url, headers=self.headers, params=params, timeout=15) # Increased timeout
            
            print(f"DEBUG: Received response status: {response.status_code}")
            if response.status_code == 200:
                print(f"DEBUG: Response JSON: {response.json()}")
                return response.json()
            else:
                print(f"GitHub API non-200 response: {response.status_code} - {response.text}")
                response.raise_for_status() # Raise HTTPError for other non-200 responses

        except requests.exceptions.HTTPError as e:
            print(f"GitHub API HTTP error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.ConnectionError as e:
            print(f"GitHub API Connection error: {e}")
        except requests.exceptions.Timeout as e:
            print(f"GitHub API Timeout error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"GitHub API Request error: {e}")
        return None

    def search_users(self, query: str, page: int = 1, per_page: int = 30) -> Optional[Dict]:
        url = f"{self.BASE_URL}/search/users"
        params = {
            "q": query,
            "page": page,
            "per_page": per_page
        }
        print(f"Searching GitHub users with query: {query}, page: {page}")
        return self._make_request("GET", url, params)

    def search_repositories(self, query: str, page: int = 1, per_page: int = 30) -> Optional[Dict]:
        url = f"{self.BASE_URL}/search/repositories"
        params = {
            "q": query,
            "page": page,
            "per_page": per_page
        }
        print(f"Searching GitHub repositories with query: {query}, page: {page}")
        return self._make_request("GET", url, params)

    def get_user_profile(self, username: str) -> Optional[Dict]:
        url = f"{self.BASE_URL}/users/{username}"
        print(f"Fetching GitHub profile for: {username}")
        return self._make_request("GET", url)

    def get_user_repos(self, username: str, page: int = 1, per_page: int = 100) -> Optional[List[Dict]]:
        url = f"{self.BASE_URL}/users/{username}/repos"
        params = {
            "page": page,
            "per_page": per_page
        }
        print(f"Fetching GitHub repos for: {username}, page: {page}")
        return self._make_request("GET", url, params) 