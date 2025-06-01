from typing import Dict, List, Optional
from src.core.models import SearchParams

class LinkedInSearchQueryGenerator:
    @staticmethod
    def generate_linkedin_search_query(params: SearchParams) -> str:
        """
        Generates a LinkedIn search query based on the parsed SearchParams.
        For now, this will create a simple keyword-based query. 
        Future iterations might incorporate more advanced LinkedIn search operators.
        """
        query_parts = []

        if params.title:
            query_parts.append(params.title)
        if params.skills:
            query_parts.extend(params.skills)
        if params.location:
            # LinkedIn often uses specific location formats, this is a simplified approach
            if isinstance(params.location, list):
                query_parts.extend(params.location)
            else:
                query_parts.append(params.location)
        if params.experience_level:
            query_parts.append(params.experience_level)
        if params.work_type:
            if isinstance(params.work_type, list):
                query_parts.extend(params.work_type)
            else:
                query_parts.append(params.work_type)

        # Filter out any None or empty strings from the parts
        cleaned_query_parts = [part.strip() for part in query_parts if part and part.strip()]

        # Join with AND for a more restrictive search, or space for a broader search
        # For now, a simple space separation
        return " ".join(cleaned_query_parts) 