import os
from openai import OpenAI

class OpenRouterClient:
    def __init__(self, api_key: str, model: str = "google/gemma-3-4b-it:free"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def complete(self, prompt: str) -> str:
        messages = [
            {"role": "user", "content": prompt}
        ]
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0,
                max_tokens=512
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"OpenRouter API error: {e}")
            raise
