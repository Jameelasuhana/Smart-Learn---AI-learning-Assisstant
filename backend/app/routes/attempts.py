from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId

from app.database import get_database
from app.schemas.test_schemas import AttemptResponse, AnswerReviewSchema
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/attempts", tags=["Attempt History"])

@router.get("", response_model=List[AttemptResponse])
async def get_attempts(current_user: dict = Depends(get_current_user)):
    db = get_database()
    if db is None:
        return []

    cursor = db["attempts"].find({"user_id": current_user["id"]}).sort("created_at", -1)
    attempts = await cursor.to_list(length=100)

    res = []
    for a in attempts:
        res.append(
            AttemptResponse(
                id=str(a["_id"]),
                test_id=a.get("test_id", ""),
                user_id=a.get("user_id", ""),
                attempt_number=a.get("attempt_number", 1),
                score=a.get("score", 0),
                total_questions=a.get("total_questions", 0),
                percentage=a.get("percentage", 0.0),
                correct_count=a.get("correct_count", 0),
                incorrect_count=a.get("incorrect_count", 0),
                unanswered_count=a.get("unanswered_count", 0),
                reviews=[AnswerReviewSchema(**r) for r in a.get("reviews", [])],
                created_at=a.get("created_at", datetime.utcnow())
            )
        )
    return res

@router.get("/{attempt_id}", response_model=AttemptResponse)
async def get_attempt_detail(
    attempt_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    try:
        attempt = await db["attempts"].find_one({"_id": ObjectId(attempt_id), "user_id": current_user["id"]})
    except Exception:
        attempt = await db["attempts"].find_one({"_id": attempt_id, "user_id": current_user["id"]})

    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt record not found.")

    return AttemptResponse(
        id=str(attempt["_id"]),
        test_id=attempt.get("test_id", ""),
        user_id=attempt.get("user_id", ""),
        attempt_number=attempt.get("attempt_number", 1),
        score=attempt.get("score", 0),
        total_questions=attempt.get("total_questions", 0),
        percentage=attempt.get("percentage", 0.0),
        correct_count=attempt.get("correct_count", 0),
        incorrect_count=attempt.get("incorrect_count", 0),
        unanswered_count=attempt.get("unanswered_count", 0),
        reviews=[AnswerReviewSchema(**r) for r in attempt.get("reviews", [])],
        created_at=attempt.get("created_at", datetime.utcnow())
    )
