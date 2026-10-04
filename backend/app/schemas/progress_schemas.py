from typing import List, Dict, Optional
from pydantic import BaseModel

class DifficultyBreakdown(BaseModel):
    attempted: int = 0
    correct: int = 0
    percentage: float = 0.0

class RecentAttemptSummary(BaseModel):
    attempt_id: str
    test_id: str
    test_title: str
    score: int
    total_questions: int
    percentage: float
    created_at: str

class ProgressResponse(BaseModel):
    tests_attempted: int
    questions_attempted: int
    average_score_percentage: float
    best_score_percentage: float
    total_correct: int
    total_incorrect: int
    total_unanswered: int
    by_difficulty: Dict[str, DifficultyBreakdown]
    recent_attempts: List[RecentAttemptSummary]

class RecommendationItem(BaseModel):
    category: str
    title: str
    description: str
    action_type: str  # e.g., "review", "practice", "generate"

class RecommendationResponse(BaseModel):
    overall_status: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[RecommendationItem]
