from typing import Dict, List
from fastapi import APIRouter, HTTPException, status, Depends
from app.database import get_database
from app.schemas.progress_schemas import ProgressResponse, RecommendationResponse, DifficultyBreakdown, RecentAttemptSummary
from app.services.gemini_service import generate_learning_recommendations
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api", tags=["Analytics & Progress"])

async def calculate_student_analytics(user_id: str) -> Dict:
    db = get_database()
    if db is None:
        return {
            "tests_attempted": 0,
            "questions_attempted": 0,
            "average_score_percentage": 0.0,
            "best_score_percentage": 0.0,
            "total_correct": 0,
            "total_incorrect": 0,
            "total_unanswered": 0,
            "by_difficulty": {},
            "recent_attempts": []
        }

    cursor = db["attempts"].find({"user_id": user_id}).sort("created_at", -1)
    attempts = await cursor.to_list(length=200)

    if not attempts:
        return {
            "tests_attempted": 0,
            "questions_attempted": 0,
            "average_score_percentage": 0.0,
            "best_score_percentage": 0.0,
            "total_correct": 0,
            "total_incorrect": 0,
            "total_unanswered": 0,
            "by_difficulty": {
                "easy": {"attempted": 0, "correct": 0, "percentage": 0.0},
                "medium": {"attempted": 0, "correct": 0, "percentage": 0.0},
                "hard": {"attempted": 0, "correct": 0, "percentage": 0.0}
            },
            "recent_attempts": []
        }

    tests_cnt = len(attempts)
    questions_cnt = sum(a.get("total_questions", 0) for a in attempts)
    percentages = [a.get("percentage", 0.0) for a in attempts]
    avg_score = round(sum(percentages) / len(percentages), 2) if percentages else 0.0
    best_score = round(max(percentages), 2) if percentages else 0.0

    total_correct = sum(a.get("correct_count", 0) for a in attempts)
    total_incorrect = sum(a.get("incorrect_count", 0) for a in attempts)
    total_unanswered = sum(a.get("unanswered_count", 0) for a in attempts)

    # Difficulty tracking
    diff_stats = {
        "easy": {"attempted": 0, "correct": 0},
        "medium": {"attempted": 0, "correct": 0},
        "hard": {"attempted": 0, "correct": 0}
    }

    for a in attempts:
        for r in a.get("reviews", []):
            d = str(r.get("difficulty", "medium")).lower()
            if d not in diff_stats:
                diff_stats[d] = {"attempted": 0, "correct": 0}
            diff_stats[d]["attempted"] += 1
            if r.get("is_correct"):
                diff_stats[d]["correct"] += 1

    by_diff_result = {}
    for d, s in diff_stats.items():
        att = s["attempted"]
        corr = s["correct"]
        pct = round((corr / att * 100), 2) if att > 0 else 0.0
        by_diff_result[d] = DifficultyBreakdown(attempted=att, correct=corr, percentage=pct)

    recent_summary = []
    for a in attempts[:10]:
        created_str = a.get("created_at").strftime("%Y-%m-%d %H:%M") if a.get("created_at") else "Recently"
        recent_summary.append(
            RecentAttemptSummary(
                attempt_id=str(a["_id"]),
                test_id=a.get("test_id", ""),
                test_title=a.get("test_title", "Smart Test"),
                score=a.get("score", 0),
                total_questions=a.get("total_questions", 0),
                percentage=a.get("percentage", 0.0),
                created_at=created_str
            )
        )

    return {
        "tests_attempted": tests_cnt,
        "questions_attempted": questions_cnt,
        "average_score_percentage": avg_score,
        "best_score_percentage": best_score,
        "total_correct": total_correct,
        "total_incorrect": total_incorrect,
        "total_unanswered": total_unanswered,
        "by_difficulty": by_diff_result,
        "recent_attempts": recent_summary
    }

@router.get("/progress", response_model=ProgressResponse)
async def get_progress(current_user: dict = Depends(get_current_user)):
    data = await calculate_student_analytics(current_user["id"])
    return ProgressResponse(**data)

@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(current_user: dict = Depends(get_current_user)):
    stats = await calculate_student_analytics(current_user["id"])
    try:
        rec_data = await generate_learning_recommendations(stats)
        return RecommendationResponse(**rec_data)
    except Exception as e:
        # Fallback recommendations if AI call fails
        avg = stats.get("average_score_percentage", 0)
        return RecommendationResponse(
            overall_status="Keep building your knowledge with regular practice quizzes!",
            strengths=["Active learning platform participation"],
            weaknesses=["Complete more tests to unlock deeper topic-level insights."],
            recommendations=[
                {
                    "category": "Practice",
                    "title": "Generate a YouTube MCQ Test",
                    "description": "Transform any educational video into a custom test to gauge your recall.",
                    "action_type": "generate"
                },
                {
                    "category": "Concept",
                    "title": "Ask AI Educational Questions",
                    "description": "Clarify challenging topics using the AI Question Answering tool.",
                    "action_type": "review"
                }
            ]
        )
