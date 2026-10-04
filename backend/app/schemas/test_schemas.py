from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class QuestionSchema(BaseModel):
    id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str  # "option_a", "option_b", "option_c", "option_d"
    explanation: str
    difficulty: str  # "easy", "medium", "hard"

class QuestionPublicSchema(BaseModel):
    id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    difficulty: str

class TestGenerateRequest(BaseModel):
    youtube_urls: List[str] = Field(..., min_items=1, description="List of YouTube URLs to extract content from")
    question_count: int = Field(20, description="Number of questions: 20, 40, 60, or 100")
    difficulty: str = Field("mixed", description="Difficulty level: easy, medium, hard, mixed")
    title: Optional[str] = None

class TestResponse(BaseModel):
    id: str
    user_id: str
    title: str
    youtube_urls: List[str]
    question_count: int
    difficulty: str
    questions: List[QuestionPublicSchema]
    created_at: datetime

class TestSubmitRequest(BaseModel):
    answers: Dict[str, str] = Field(..., description="Map of question_id (as string) to selected option ('option_a', 'option_b', etc.)")

class AnswerReviewSchema(BaseModel):
    question_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    selected_answer: Optional[str] = None
    correct_answer: str
    is_correct: bool
    explanation: str
    difficulty: str

class AttemptResponse(BaseModel):
    id: str
    test_id: str
    user_id: str
    attempt_number: int
    score: int
    total_questions: int
    percentage: float
    correct_count: int
    incorrect_count: int
    unanswered_count: int
    reviews: List[AnswerReviewSchema]
    created_at: datetime

class ReattemptRequest(BaseModel):
    test_id: str

class PracticeIncorrectRequest(BaseModel):
    test_id: str
