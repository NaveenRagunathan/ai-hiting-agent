from typing import List, Dict, Optional
from src.connectors.github_agent.github_fetcher import GitHubFetcher
from src.connectors.github_agent.models import GitHubSearchUserResult, GitHubUserProfile, GitHubRepo

class ProfileCollector:
    def __init__(self, github_fetcher: GitHubFetcher):
        self.github_fetcher = github_fetcher

    def collect_profiles(self, user_search_results: List[GitHubSearchUserResult]) -> List[Dict]:
        collected_profiles = []
        print(f"Collecting detailed profiles for {len(user_search_results)} users...")

        for user_result in user_search_results:
            username = user_result.login
            print(f"  -> Collecting data for user: {username}")

            profile_data = self.github_fetcher.get_user_profile(username)
            repo_data = self.github_fetcher.get_user_repos(username)

            if profile_data and repo_data is not None: # Check if repo_data is not None (can be empty list)
                collected_profiles.append({
                    "user_profile": GitHubUserProfile(**profile_data).dict(),
                    "user_repos": [GitHubRepo(**repo).dict() for repo in repo_data]
                })
            elif profile_data:
                print(f"    Warning: No public repositories found for {username}, collecting profile only.")
                collected_profiles.append({
                    "user_profile": GitHubUserProfile(**profile_data).dict(),
                    "user_repos": [] # Empty list if no repos
                })
            else:
                print(f"    Error: Failed to collect profile for {username}. Skipping.")

        return collected_profiles 