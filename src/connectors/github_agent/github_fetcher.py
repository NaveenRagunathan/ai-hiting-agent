import os
import time
import logging
import requests
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimitExceeded(Exception):
    """Raised when GitHub API rate limit is exceeded."""
    pass

class GitHubFetcher:
    BASE_URL = "https://api.github.com"
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 2  # seconds
    
    def __init__(self, github_token: Optional[str] = None):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.rate_limit_remaining = 30  # Default unauthenticated limit
        self.rate_limit_reset = datetime.now()
        
        if github_token:
            self.headers["Authorization"] = f"Bearer {github_token}"
            self.rate_limit_remaining = 30  # Higher limit for authenticated requests
        else:
            logger.warning(
                "GitHub token is missing. API requests will be unauthenticated "
                "and subject to severe rate limits (60 requests/hour)."
            )
    
    def _check_rate_limit(self):
        """Check if we've hit the rate limit and need to wait."""
        if self.rate_limit_remaining <= 1:  # Leave some buffer
            reset_in = (self.rate_limit_reset - datetime.now()).total_seconds()
            if reset_in > 0:
                logger.warning(f"Rate limit reached. Waiting {reset_in:.1f} seconds...")
                time.sleep(max(1, reset_in))  # Wait at least 1 second
    
    def _update_rate_limit(self, headers: Dict[str, str]):
        """Update rate limit information from response headers."""
        if 'X-RateLimit-Remaining' in headers:
            self.rate_limit_remaining = int(headers['X-RateLimit-Remaining'])
            
        if 'X-RateLimit-Reset' in headers:
            reset_timestamp = int(headers['X-RateLimit-Reset'])
            self.rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
    
    def _make_request(
        self, 
        method: str, 
        url: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Tuple[Optional[Dict], Optional[int]]:
        """
        Make an HTTP request with retry logic and rate limit handling.
        
        Returns:
            Tuple of (response_json, status_code)
        """
        try:
            self._check_rate_limit()
            
            logger.debug(f"Making {method} request to {url} with params: {params}")
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=30  # Increased timeout
            )
            
            # Update rate limit information
            self._update_rate_limit(response.headers)
            
            status_code = response.status_code
            logger.debug(f"Response status: {status_code}")
            
            # Handle rate limiting
            if status_code == 403 and 'rate limit exceeded' in response.text.lower():
                if retry_count < self.MAX_RETRIES:
                    retry_after = int(response.headers.get('Retry-After', self.INITIAL_RETRY_DELAY * (retry_count + 1)))
                    logger.warning(f"Rate limited. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    return self._make_request(method, url, params, data, retry_count + 1)
                raise RateLimitExceeded("Rate limit exceeded and max retries reached")
                
            # Handle other error statuses
            if status_code >= 400:
                error_msg = f"GitHub API error {status_code}: {response.text}"
                if status_code == 404:
                    logger.warning(error_msg)
                else:
                    logger.error(error_msg)
                return None, status_code
                
            # Parse JSON response
            try:
                return response.json(), status_code
            except ValueError:
                logger.error(f"Failed to parse JSON response: {response.text}")
                return None, status_code
                
        except requests.exceptions.RequestException as e:
            if retry_count < self.MAX_RETRIES:
                delay = self.INITIAL_RETRY_DELAY * (2 ** retry_count)  # Exponential backoff
                logger.warning(f"Request failed: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
                return self._make_request(method, url, params, data, retry_count + 1)
            logger.error(f"Request failed after {self.MAX_RETRIES} retries: {e}")
            return None, None

    def search_repositories(
        self, 
        query: str, 
        page: int = 1, 
        per_page: int = 30,
        max_pages: int = 3
    ) -> Dict[str, Any]:
        """
        Search GitHub repositories with pagination support.
        
        Args:
            query: Search query string
            page: Page number to start from (1-based)
            per_page: Number of results per page (max 100)
            max_pages: Maximum number of pages to fetch
            
        Returns:
            Dictionary containing search results and metadata
        """
        url = f"{self.BASE_URL}/search/repositories"
        all_items = []
        total_count = 0
        
        for current_page in range(page, page + max_pages):
            params = {
                "q": query,
                "page": current_page,
                "per_page": min(100, per_page),  # GitHub max is 100
                "sort": "stars",
                "order": "desc"
            }
            
            result, status_code = self._make_request("GET", url, params=params)
            
            if not result or 'items' not in result:
                logger.warning(f"No results or error in page {current_page}")
                break
                
            items = result.get('items', [])
            all_items.extend(items)
            total_count = result.get('total_count', 0)
            
            # Stop if we've got enough results or there are no more pages
            if len(all_items) >= per_page or len(items) < params['per_page']:
                break
        
        return {
            'total_count': total_count,
            'incomplete_results': len(all_items) < total_count,
            'items': all_items[:per_page]  # Return only the requested number of items
        }

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