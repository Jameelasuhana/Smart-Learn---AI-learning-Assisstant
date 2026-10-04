from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class AttemptModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    test_id: str
    test_title: str
    attempt_number: int
    selected_answers: Dict[str, str]  # question_id_str -> selected_option
    score: int
    total_questions: int
    percentage: float
    correct_count: int
    incorrect_count: int
    unanswered_count: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
