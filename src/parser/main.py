from fastapi import FastAPI, HTTPException
from src.parser.models import ParseQueryRequest, ParseQueryResponse
from src.parser.parsing_agent.llm_parser import LLMParserAgent
from src.parser.parsing_agent.groq_client import OpenRouterClient
from src.parser.parsing_agent.validator import Validator
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
llm_agent = LLMParserAgent(OpenRouterClient(api_key=openrouter_api_key))

@app.post("/parse-query", response_model=ParseQueryResponse)
def parse_query(request: ParseQueryRequest):
    try:
        parsed = llm_agent.parse(request.query)
        validated = Validator.validate(parsed)
        return ParseQueryResponse(**validated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 