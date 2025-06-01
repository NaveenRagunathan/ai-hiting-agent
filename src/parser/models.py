from pydantic import BaseModel, Field
from typing import List, Optional, Union

class ParseQueryRequest(BaseModel):
    query: str = Field(..., description="The raw user query to parse.")

class ParseQueryResponse(BaseModel):
    intent: str
    title: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    location: Optional[Union[str, List[str]]] = None
    work_type: Optional[Union[str, List[str]]] = None 