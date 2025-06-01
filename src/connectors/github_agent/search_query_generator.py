from typing import List, Optional, Dict, Union

class SearchQueryGenerator:
    @staticmethod
    def generate_github_repo_search_query(parsed_nlp_output: Dict) -> str:
        query_parts = []

        # Helper to safely add parts, ignoring empty/unspecified values
        def _add_to_query_parts(value: Optional[Union[str, List[str]]], prefix: str = "", field_type: str = "keyword"):
            if value:
                if isinstance(value, list):
                    for item in value:
                        if item and item.lower() != "unspecified":
                            if field_type == "language":
                                query_parts.append(f"language:{item}")
                            elif field_type == "topic":
                                query_parts.append(f"topic:{item}")
                            elif field_type == "location":
                                query_parts.append(f"location:{item}") # Still applicable if searching user profiles later
                            else: # default to keyword
                                query_parts.append(item)
                elif isinstance(value, str):
                    if value.lower() != "unspecified":
                        if field_type == "language":
                            query_parts.append(f"language:{value}")
                        elif field_type == "topic":
                            query_parts.append(f"topic:{value}")
                        elif field_type == "location":
                            query_parts.append(f"location:{value}")
                        else: # default to keyword
                            query_parts.append(value)

        # Add title keywords to search in repo name/description
        title = parsed_nlp_output.get("title")
        _add_to_query_parts(title) # Default to keyword

        # Add skills as general keywords or topics if clear
        skills = parsed_nlp_output.get("skills")
        _add_to_query_parts(skills, field_type="topic") # Prefer topics for skills if possible
        _add_to_query_parts(skills) # Also add as general keywords

        # Add location (as a keyword, GitHub repo search doesn't have direct location for owner)
        # We will use this in the next step when fetching user profiles.
        # _add_to_query_parts(parsed_nlp_output.get("location"), prefix="location:") # This is for user search

        # Combine all parts with '+' for URL encoding
        github_query = "+".join(query_parts)

        # Add default filters for repositories
        if "fork:true" not in github_query and "fork:false" not in github_query:
             # Prefer non-forked repos unless specified
            github_query += "+fork:true"
        
        # Add a minimum number of stars as a basic filter for relevant repos
        if "stars:>" not in github_query:
            github_query += "+stars:>1"

        # Fallback if query_parts ends up empty
        if not github_query.strip() or github_query.strip() == "stars:>1+fork:true":
            return "language:Python+stars:>10" # Broad search for Python repos as a robust default

        return github_query.strip()

    # Removed generate_github_user_search_query as we're shifting focus

    # Could add methods for search/code if needed later
    # @staticmethod
    # def generate_github_code_search_query(parsed_nlp_output: Dict) -> str:
    #     pass 