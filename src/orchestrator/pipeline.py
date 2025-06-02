import pdfplumber
import re

class ResumeOrchestrator:
    def __init__(self):
        pass

    def process_resume_batch(self, resume_files: list, job_description: str):
        results = []
        for resume_file in resume_files:
            result = self.process_single_resume(resume_file, job_description)
            results.append(result)
        return results

    def process_single_resume(self, resume_file, job_description):
        # 1. Extract data from resume
        resume_data = self.extract_resume_data(resume_file)
        # 2. ATS analysis
        ats_result = self.ats_analysis(resume_data)
        # 3. Generate NLP query
        nlp_query = self.generate_nlp_query(resume_data)
        # 4. Fetch LinkedIn & GitHub data
        linkedin_profile = self.fetch_linkedin_profile(nlp_query)
        github_profile = self.fetch_github_profile(nlp_query)
        # 5. JD analysis
        jd_analysis = self.analyze_jd(job_description, resume_data, linkedin_profile, github_profile)
        # 6. SWOT analysis
        swot_report = self.generate_swot(jd_analysis)
        # 7. Aggregate results
        return {
            "resume_data": resume_data,
            "ats_result": ats_result,
            "linkedin_profile": linkedin_profile,
            "github_profile": github_profile,
            "jd_analysis": jd_analysis,
            "swot_report": swot_report,
        }

    def extract_resume_data(self, resume_file):
        """
        Extracts structured data from a PDF resume file.
        Args:
            resume_file: Path to the PDF file or a file-like object.
        Returns:
            dict: Extracted fields (name, email, phone, etc.)
        """
        text = ""
        with pdfplumber.open(resume_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        # Simple regex-based extraction
        email = re.search(r"[\w\.-]+@[\w\.-]+", text)
        phone = re.search(r"(\+?\d[\d\s\-]{7,}\d)", text)
        # Name extraction is non-trivial; as a placeholder, use the first non-empty line
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        name = lines[0] if lines else None
        return {
            "raw_text": text,
            "name": name,
            "email": email.group(0) if email else None,
            "phone": phone.group(0) if phone else None,
            # Add more fields as needed
        }

    def ats_analysis(self, resume_data):
        """
        Analyzes resume text for ATS compatibility.
        Returns a dict with a score and a list of issues.
        """
        text = resume_data.get("raw_text", "").lower()
        issues = []
        score = 0
        # Check for key sections
        for section in ["education", "experience", "skills"]:
            if section not in text:
                issues.append(f"Missing section: {section.title()}")
            else:
                score += 1
        # Example: count keyword matches (expandable)
        keywords = ["python", "machine learning", "project", "leadership"]
        keyword_matches = sum(1 for kw in keywords if kw in text)
        score += keyword_matches
        if keyword_matches < 2:
            issues.append("Few relevant keywords found.")
        return {
            "score": score,
            "issues": issues,
            "keyword_matches": keyword_matches
        }

    def generate_nlp_query(self, resume_data):
        """
        Generates a search query from resume data for use by LinkedIn/GitHub agents.
        Returns a dict with relevant fields.
        """
        # For now, use name, skills, and experience if available
        query = {}
        if resume_data.get("name"):
            query["name"] = resume_data["name"]
        # Skills extraction can be improved; for now, look for a 'skills' section in raw_text
        skills = []
        text = resume_data.get("raw_text", "")
        skills_section = re.search(r"skills[:\-\s]*([\w,\s]+)", text, re.IGNORECASE)
        if skills_section:
            skills = [s.strip() for s in skills_section.group(1).split(",") if s.strip()]
        if skills:
            query["skills"] = skills
        # Experience extraction placeholder
        # (Can use NLP or section parsing for more accuracy)
        return query

    def fetch_linkedin_profile(self, nlp_query):
        """
        Uses the LinkedIn agent to fetch and normalize a LinkedIn profile based on the NLP query.
        Returns a CandidateProfile or None.
        """
        from src.connectors.linkedin_agent.linkedin_fetcher import LinkedInFetcher
        from src.connectors.linkedin_agent.search_query_generator import LinkedInSearchQueryGenerator
        from src.connectors.linkedin_agent.profile_normalizer import LinkedInProfileNormalizer
        from src.connectors.linkedin_agent.models import LinkedInRawProfile
        from src.core.models import SearchParams

        # Build SearchParams from nlp_query (fill with defaults if missing)
        params = SearchParams(
            intent="find_candidates",
            title=nlp_query.get("title"),
            skills=nlp_query.get("skills"),
            experience_level=nlp_query.get("experience_level"),
            location=nlp_query.get("location"),
            work_type=nlp_query.get("work_type"),
        )
        linkedin_query = LinkedInSearchQueryGenerator.generate_linkedin_search_query(params)
        fetcher = LinkedInFetcher()
        raw_profile_results = fetcher.search_profiles(linkedin_query)
        if not raw_profile_results:
            return None
        # Get details for the first profile
        detailed_raw_profile = fetcher.get_profile_details(raw_profile_results[0].get("profile_url"))
        if not detailed_raw_profile:
            return None
        linkedin_raw_profile_model = LinkedInRawProfile(**detailed_raw_profile)
        normalized_profile = LinkedInProfileNormalizer.normalize_profile(linkedin_raw_profile_model)
        return normalized_profile

    def fetch_github_profile(self, nlp_query):
        """
        Uses the GitHub agent to fetch and normalize a GitHub profile based on the NLP query.
        Returns a CandidateProfile or None.
        """
        from src.connectors.github_agent.cli import run_github_search
        candidates = run_github_search(nlp_query)
        if not candidates:
            return None
        return candidates[0]

    def analyze_jd(self, job_description, resume_data, linkedin_profile, github_profile):
        """
        Analyzes the fit between the job description and the candidate's profile.
        Returns a dict with matches, gaps, and a fit score.
        """
        jd_text = job_description.lower()
        # Aggregate candidate skills from all sources
        candidate_skills = set()
        for source in [resume_data, linkedin_profile, github_profile]:
            if source and source.get("skills"):
                candidate_skills.update([s.lower() for s in source["skills"]])
        # Extract keywords from JD (simple split, can be improved)
        jd_keywords = set([w.strip('.,') for w in jd_text.split() if len(w) > 2])
        matches = candidate_skills & jd_keywords
        gaps = jd_keywords - candidate_skills
        fit_score = len(matches) / (len(jd_keywords) or 1)
        return {
            "matches": list(matches),
            "gaps": list(gaps),
            "fit_score": fit_score
        }

    def generate_swot(self, jd_analysis):
        """
        Generates a simple SWOT analysis from the JD analysis.
        Returns a dict with strengths, weaknesses, opportunities, and threats.
        """
        strengths = jd_analysis.get("matches", [])
        weaknesses = jd_analysis.get("gaps", [])
        opportunities = ["Potential to learn missing skills", "Growth in new areas"]
        threats = ["High competition for this role", "Skill gaps may affect shortlisting"]
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "threats": threats
        } 