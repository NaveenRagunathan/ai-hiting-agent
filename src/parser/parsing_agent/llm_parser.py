import json
import re

class LLMParserAgent:
    def __init__(self, groq_client):
        self.groq_client = groq_client

    def build_prompt(self, query: str) -> str:
        return f"""You are an AI recruiter assistant. Convert the following user query into structured hiring parameters.\n\nInput:\n\"{query}\"\n\nReturn a JSON object with the following fields:\n- intent\n- title\n- skills\n- experience_level\n- location\n- work_type\n\nBe strict about formatting. Only return valid JSON.\n\nOutput:"""

    def parse(self, query: str) -> dict:
        prompt = self.build_prompt(query)
        llm_response = self.groq_client.complete(prompt)
        
        # Attempt to extract JSON from a markdown code block first
        json_match = re.search(r"```json\n(.*?)```", llm_response, re.DOTALL)
        if json_match:
            json_string = json_match.group(1)
        else:
            # If no markdown block, assume the whole response is JSON
            json_string = llm_response.strip()

        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from LLM response: {e}")
            print(f"Problematic JSON string: \n---\n{json_string}\n---")
            raise ValueError(f"Failed to parse LLM response as JSON: {e}") 