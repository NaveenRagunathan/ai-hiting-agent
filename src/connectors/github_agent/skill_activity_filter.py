from typing import List, Dict, Optional
import datetime

class SkillActivityFilter:
    @staticmethod
    def extract_skills(profile_data: Dict, repo_data: List[Dict]) -> List[str]:
        skills = set()
        
        # From repo languages
        for repo in repo_data:
            if repo.get("language"):
                skills.add(repo["language"])
        
        # From repo topics (if available)
        for repo in repo_data:
            for topic in repo.get("topics", []):
                skills.add(topic)

        # From repo descriptions and user bio (basic keyword matching)
        keywords = ["AI", "ML", "Gen-AI", "Machine Learning", "Artificial Intelligence", 
                    "LangChain", "RAG", "LLM", "NLP", "Deep Learning", "Python", "TensorFlow", "PyTorch"]
        
        bio = profile_data.get("bio", "").lower()
        for keyword in keywords:
            if keyword.lower() in bio:
                skills.add(keyword)

        for repo in repo_data:
            description = repo.get("description", "").lower()
            for keyword in keywords:
                if keyword.lower() in description:
                    skills.add(keyword)
                    
        return list(skills)

    @staticmethod
    def analyze_activity(profile_data: Dict, repo_data: List[Dict]) -> Dict:
        total_stars = 0
        top_languages = {}
        last_active_timestamp: Optional[datetime.datetime] = None

        for repo in repo_data:
            total_stars += repo.get("stargazers_count", 0)
            if repo.get("language"):
                lang = repo["language"]
                top_languages[lang] = top_languages.get(lang, 0) + 1
            
            # Track recent activity from repo push timestamps
            updated_at_str = repo.get("updated_at")
            if updated_at_str:
                try:
                    updated_at = datetime.datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                    if last_active_timestamp is None or updated_at > last_active_timestamp:
                        last_active_timestamp = updated_at
                except ValueError:
                    pass # Handle malformed dates

        # Basic OSS score (can be refined)
        followers = profile_data.get("followers", 0)
        public_repos = profile_data.get("public_repos", 0)
        oss_score = (total_stars * 0.5) + (followers * 0.3) + (public_repos * 0.2)

        sorted_languages = sorted(top_languages.items(), key=lambda item: item[1], reverse=True)
        
        return {
            "total_stars": total_stars,
            "top_languages": [lang for lang, _ in sorted_languages[:5]], # Top 5 languages
            "recent_activity": last_active_timestamp.isoformat() if last_active_timestamp else None,
            "oss_score": int(oss_score) # Convert to int for simplicity
        }

    @staticmethod
    def apply_filters(candidate_data: Dict, required_activity_months: int = 12) -> bool:
        # Filter by recent activity
        recent_activity_str = candidate_data.get("recent_activity")
        if recent_activity_str:
            try:
                recent_activity = datetime.datetime.fromisoformat(recent_activity_str.replace("Z", "+00:00"))
                six_months_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30 * required_activity_months)
                if recent_activity < six_months_ago:
                    print(f"Filtering out {candidate_data.get('github_username')}: Last activity too old.")
                    return False
            except ValueError:
                print(f"Filtering out {candidate_data.get('github_username')}: Invalid recent_activity timestamp.")
                return False
        else:
            print(f"Filtering out {candidate_data.get('github_username')}: No recent activity found.")
            return False
            
        # You can add more filters here (e.g., minimum stars, specific skills required)

        return True 