# HireAI Parser

A dynamic, LLM-powered natural language parser for hiring queries. Uses OpenRouter.ai for LLM intent/entity extraction and outputs structured, query-ready JSON.

## Features
- LLM-first: No static rules, pure LLM extraction
- Handles complex, multi-intent prompts
- FastAPI endpoint for easy integration
- OpenRouter.ai for flexible LLM access

## Setup
1. Clone this repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root (`hireai_parser/`) and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=sk-or-v1-YOUR-OPENROUTER-API-KEY
   ```

## Run the API
```bash
uvicorn hireai_parser.main:app --reload
```

## Test with Sample Queries
```bash
python hireai_parser/test_queries.py
```

## API Usage
POST `/parse-query`
```json
{
  "query": "Find senior Gen-AI engineers with LangChain + RAG experience in Europe, open to contract work"
}
```

Response:
```json
{
  "intent": "find",
  "title": "Gen-AI Engineer",
  "skills": ["LangChain", "RAG"],
  "experience_level": "senior",
  "location": "Europe",
  "work_type": "contract"
}
``` 