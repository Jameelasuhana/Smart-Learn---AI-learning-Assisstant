from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.test_schemas import QuestionSchema

class TestModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    title: str
    youtube_urls: List[str]
    question_count: int
    difficulty: str
    questions: List[QuestionSchema]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
