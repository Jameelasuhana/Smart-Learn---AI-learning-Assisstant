from typing import List, Optional
from pydantic import BaseModel, Field

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000, description="Educational question to ask AI")

class QuestionResponse(BaseModel):
    question: str
    answer: str
    key_takeaways: Optional[List[str]] = []

class ExplainRequest(BaseModel):
    concept: str = Field(..., min_length=2, max_length=500, description="Educational concept name")
    level: str = Field("intermediate", description="Target level: beginner, intermediate, advanced")

class ExplainResponse(BaseModel):
    concept: str
    level: str
    explanation: str
    analogies: Optional[List[str]] = []
    key_points: Optional[List[str]] = []

class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=50000, description="Educational text to summarize")

class SummarizeResponse(BaseModel):
    summary: str
    key_points: List[str]
    important_concepts: List[str]
    key_terms: List[dict]  # list of {"term": ..., "definition": ...}
