import logging
from typing import List, Optional, Dict, Union
import urllib.parse

logger = logging.getLogger(__name__)


class SearchQueryGenerator:
    @staticmethod
    def _clean_query_term(term: str) -> str:
        """Clean and encode query terms."""
        # Remove special characters that might break the query
        term = ''.join(c for c in term if c.isalnum() or c in ['-', '_', '.', ' '])
        # Replace spaces with hyphens for topics and encode the rest
        return urllib.parse.quote_plus(term.strip())

    @staticmethod
    def _build_search_terms(terms: Union[str, List[str]], field: str = None) -> List[str]:
        """Build search terms with optional field prefix."""
        if not terms:
            return []
            
        if isinstance(terms, str):
            terms = [terms]
            
        search_terms = []
        for term in terms:
            if not term or term.lower() == 'unspecified':
                continue
                
            cleaned = SearchQueryGenerator._clean_query_term(term)
            if not cleaned:
                continue
                
            if field:
                if field == 'topic':
                    # For topics, replace spaces with hyphens
                    cleaned = cleaned.replace(' ', '-')
                search_terms.append(f"{field}:{cleaned}")
            else:
                search_terms.append(cleaned)
                
        return search_terms

    @staticmethod
    def generate_github_repo_search_query(parsed_nlp_output: Dict) -> str:
        """
        Generate a GitHub repository search query from parsed NLP output.
        
        Args:
            parsed_nlp_output: Dictionary containing parsed query parameters
            
        Returns:
            str: Formatted GitHub search query
        """
        try:
            query_terms = []
            
            # 1. Add title as a general search term
            if title := parsed_nlp_output.get('title'):
                query_terms.extend(SearchQueryGenerator._build_search_terms(title))
            
            # 2. Add skills as both topics and keywords
            if skills := parsed_nlp_output.get('skills'):
                # Add as topics
                query_terms.extend(SearchQueryGenerator._build_search_terms(skills, 'topic'))
                # Add as keywords
                query_terms.extend(SearchQueryGenerator._build_search_terms(skills))
            
            # 3. Add experience level if specified
            if exp_level := parsed_nlp_output.get('experience_level'):
                if exp_level.lower() != 'unspecified':
                    query_terms.append(exp_level)
            
            # 4. Join all terms with '+' for URL encoding
            github_query = '+'.join(query_terms)
            
            # 5. Add default filters 
            # github_query += '+is:public'  # Only public repos
            
            logger.debug(f"Generated GitHub search query: {github_query}")
            return github_query
            
        except Exception as e:
            logger.error(f"Error generating GitHub search query: {e}")
            # Fallback to a simple search if there's an error
            fallback = parsed_nlp_output.get('title', '') or ' '.join(parsed_nlp_output.get('skills', []))
            return urllib.parse.quote_plus(fallback.strip())
        # Fallback if query_parts ends up empty
        if not github_query.strip() or github_query.strip() == "stars:>1+fork:true":
            return "language:Python+stars:>10" # Broad search for Python repos as a robust default

        return github_query.strip()

    # Removed generate_github_user_search_query as we're shifting focus

    # Could add methods for search/code if needed later
    # @staticmethod
    # def generate_github_code_search_query(parsed_nlp_output: Dict) -> str:
    #     pass 