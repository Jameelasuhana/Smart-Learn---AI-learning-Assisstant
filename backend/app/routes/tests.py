from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId

from app.database import get_database
from app.schemas.test_schemas import (
    TestGenerateRequest, TestResponse, QuestionPublicSchema,
    TestSubmitRequest, AttemptResponse, AnswerReviewSchema,
    ReattemptRequest, PracticeIncorrectRequest
)
from app.services.youtube_service import process_youtube_urls
from app.services.gemini_service import generate_mcq_test
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/tests", tags=["Tests & Quiz"])

@router.post("/generate", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
async def generate_test(
    req: TestGenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    # Step 1: Validate URLs and Extract Transcripts
    yt_result = process_youtube_urls(req.youtube_urls)
    if yt_result["successful_videos"] == 0:
        err_msg = yt_result["video_details"][0]["error_message"] if yt_result["video_details"] else "Unable to extract transcript."
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )

    transcript = yt_result["combined_transcript"]
    if not transcript or len(transcript) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to extract a usable transcript from this video. Please try another video."
        )

    # Step 2: Generate Questions using Gemini AI
    try:
        raw_questions = await generate_mcq_test(
            transcript_text=transcript,
            question_count=req.question_count,
            difficulty=req.difficulty
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test generation failed: {str(e)}"
        )

    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable."
        )

    title = req.title or f"Smart Test ({req.difficulty.capitalize()} - {len(raw_questions)} Qs)"

    test_doc = {
        "user_id": current_user["id"],
        "title": title,
        "youtube_urls": req.youtube_urls,
        "question_count": len(raw_questions),
        "difficulty": req.difficulty,
        "questions": raw_questions,
        "created_at": datetime.utcnow()
    }

    result = await db["tests"].insert_one(test_doc)
    test_id = str(result.inserted_id)

    public_questions = [
        QuestionPublicSchema(
            id=q["id"],
            question=q["question"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            difficulty=q["difficulty"]
        ) for q in raw_questions
    ]

    return TestResponse(
        id=test_id,
        user_id=current_user["id"],
        title=title,
        youtube_urls=req.youtube_urls,
        question_count=len(public_questions),
        difficulty=req.difficulty,
        questions=public_questions,
        created_at=test_doc["created_at"]
    )

@router.get("/user/history")
async def get_user_tests(current_user: dict = Depends(get_current_user)):
    db = get_database()
    if db is None:
        return []

    cursor = db["tests"].find({"user_id": current_user["id"]}).sort("created_at", -1)
    tests = await cursor.to_list(length=100)

    results = []
    for t in tests:
        t_id = str(t["_id"])
        # Find attempts for this test
        attempts_cursor = db["attempts"].find({"test_id": t_id, "user_id": current_user["id"]}).sort("attempt_number", -1)
        attempts = await attempts_cursor.to_list(length=20)
        
        results.append({
            "id": t_id,
            "title": t.get("title", "Smart Learn Test"),
            "youtube_urls": t.get("youtube_urls", []),
            "question_count": t.get("question_count", len(t.get("questions", []))),
            "difficulty": t.get("difficulty", "mixed"),
            "created_at": t.get("created_at"),
            "total_attempts": len(attempts),
            "latest_score": attempts[0]["score"] if attempts else None,
            "latest_percentage": attempts[0]["percentage"] if attempts else None
        })

    return results

@router.get("/{test_id}", response_model=TestResponse)
async def get_test(
    test_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    try:
        test = await db["tests"].find_one({"_id": ObjectId(test_id)})
    except Exception:
        test = await db["tests"].find_one({"_id": test_id})

    if not test:
        raise HTTPException(status_code=404, detail="Test not found.")

    public_questions = [
        QuestionPublicSchema(
            id=q["id"],
            question=q["question"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            difficulty=q.get("difficulty", "medium")
        ) for q in test.get("questions", [])
    ]

    return TestResponse(
        id=str(test["_id"]),
        user_id=test["user_id"],
        title=test.get("title", "Smart Learn Test"),
        youtube_urls=test.get("youtube_urls", []),
        question_count=len(public_questions),
        difficulty=test.get("difficulty", "mixed"),
        questions=public_questions,
        created_at=test.get("created_at", datetime.utcnow())
    )

@router.post("/{test_id}/submit", response_model=AttemptResponse)
async def submit_test(
    test_id: str,
    req: TestSubmitRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    BACKEND SCORE CALCULATION:
    Never trusts client submitted score. Backend evaluates selected options against ground truth.
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    try:
        test = await db["tests"].find_one({"_id": ObjectId(test_id)})
    except Exception:
        test = await db["tests"].find_one({"_id": test_id})

    if not test:
        raise HTTPException(status_code=404, detail="Test not found.")

    questions = test.get("questions", [])
    total_q = len(questions)
    if total_q == 0:
        raise HTTPException(status_code=400, detail="Test has no questions.")

    user_answers = req.answers or {}
    correct_cnt = 0
    incorrect_cnt = 0
    unanswered_cnt = 0
    reviews = []

    for q in questions:
        q_id_str = str(q["id"])
        selected = user_answers.get(q_id_str)
        correct_ans = q.get("correct_answer", "").lower().strip()
        
        if not selected:
            unanswered_cnt += 1
            is_corr = False
        else:
            selected_clean = selected.lower().strip()
            if selected_clean == correct_ans:
                correct_cnt += 1
                is_corr = True
            else:
                incorrect_cnt += 1
                is_corr = False

        reviews.append(
            AnswerReviewSchema(
                question_id=q["id"],
                question=q["question"],
                option_a=q["option_a"],
                option_b=q["option_b"],
                option_c=q["option_c"],
                option_d=q["option_d"],
                selected_answer=selected,
                correct_answer=correct_ans,
                is_correct=is_corr,
                explanation=q.get("explanation", "No explanation provided."),
                difficulty=q.get("difficulty", "medium")
            )
        )

    score = correct_cnt
    percentage = round((correct_cnt / total_q) * 100, 2)

    # Calculate attempt number
    existing_attempts_cnt = await db["attempts"].count_documents({
        "user_id": current_user["id"],
        "test_id": test_id
    })
    attempt_num = existing_attempts_cnt + 1

    attempt_doc = {
        "user_id": current_user["id"],
        "test_id": test_id,
        "test_title": test.get("title", "Smart Learn Test"),
        "attempt_number": attempt_num,
        "selected_answers": user_answers,
        "score": score,
        "total_questions": total_q,
        "percentage": percentage,
        "correct_count": correct_cnt,
        "incorrect_count": incorrect_cnt,
        "unanswered_count": unanswered_cnt,
        "reviews": [r.dict() for r in reviews],
        "created_at": datetime.utcnow()
    }

    result = await db["attempts"].insert_one(attempt_doc)
    attempt_id = str(result.inserted_id)

    return AttemptResponse(
        id=attempt_id,
        test_id=test_id,
        user_id=current_user["id"],
        attempt_number=attempt_num,
        score=score,
        total_questions=total_q,
        percentage=percentage,
        correct_count=correct_cnt,
        incorrect_count=incorrect_cnt,
        unanswered_count=unanswered_cnt,
        reviews=reviews,
        created_at=attempt_doc["created_at"]
    )

@router.post("/{test_id}/reattempt", response_model=TestResponse)
async def reattempt_test(
    test_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Reattempt test by generating a NEW question set from the original video sources.
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    try:
        orig_test = await db["tests"].find_one({"_id": ObjectId(test_id)})
    except Exception:
        orig_test = await db["tests"].find_one({"_id": test_id})

    if not orig_test:
        raise HTTPException(status_code=404, detail="Original test not found.")

    urls = orig_test.get("youtube_urls", [])
    yt_result = process_youtube_urls(urls)
    if yt_result["successful_videos"] == 0:
        raise HTTPException(
            status_code=400,
            detail="Unable to extract video content for reattempt. Please try creating a new test."
        )

    new_questions = await generate_mcq_test(
        transcript_text=yt_result["combined_transcript"],
        question_count=orig_test.get("question_count", 20),
        difficulty=orig_test.get("difficulty", "mixed")
    )

    new_title = f"{orig_test.get('title', 'Smart Test')} (Reattempt)"
    new_test_doc = {
        "user_id": current_user["id"],
        "title": new_title,
        "youtube_urls": urls,
        "question_count": len(new_questions),
        "difficulty": orig_test.get("difficulty", "mixed"),
        "questions": new_questions,
        "created_at": datetime.utcnow()
    }

    result = await db["tests"].insert_one(new_test_doc)
    new_test_id = str(result.inserted_id)

    public_questions = [
        QuestionPublicSchema(
            id=q["id"],
            question=q["question"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            difficulty=q.get("difficulty", "medium")
        ) for q in new_questions
    ]

    return TestResponse(
        id=new_test_id,
        user_id=current_user["id"],
        title=new_title,
        youtube_urls=urls,
        question_count=len(public_questions),
        difficulty=orig_test.get("difficulty", "mixed"),
        questions=public_questions,
        created_at=new_test_doc["created_at"]
    )

@router.post("/{test_id}/practice-incorrect", response_model=TestResponse)
async def practice_incorrect(
    test_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Practice Incorrect Questions:
    Creates a new focused quiz consisting of previously missed/unanswered questions from latest attempt.
    """
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable.")

    # Find user's latest attempt for this test
    latest_attempt = await db["attempts"].find_one(
        {"test_id": test_id, "user_id": current_user["id"]},
        sort=[("created_at", -1)]
    )

    if not latest_attempt or "reviews" not in latest_attempt:
        raise HTTPException(status_code=404, detail="No previous attempt found to extract incorrect questions.")

    incorrect_reviews = [r for r in latest_attempt["reviews"] if not r.get("is_correct")]

    if not incorrect_reviews:
        raise HTTPException(
            status_code=400,
            detail="Congratulations! You scored 100% on your last attempt. No incorrect questions to practice!"
        )

    # Build practice question list
    practice_questions = []
    for idx, r in enumerate(incorrect_reviews, 1):
        practice_questions.append({
            "id": idx,
            "question": r["question"],
            "option_a": r["option_a"],
            "option_b": r["option_b"],
            "option_c": r["option_c"],
            "option_d": r["option_d"],
            "correct_answer": r["correct_answer"],
            "explanation": r["explanation"],
            "difficulty": r.get("difficulty", "medium")
        })

    title = f"Practice: Missed Questions ({len(practice_questions)} Qs)"
    practice_doc = {
        "user_id": current_user["id"],
        "title": title,
        "youtube_urls": [],
        "question_count": len(practice_questions),
        "difficulty": "mixed",
        "questions": practice_questions,
        "created_at": datetime.utcnow()
    }

    result = await db["tests"].insert_one(practice_doc)
    new_id = str(result.inserted_id)

    public_q = [
        QuestionPublicSchema(
            id=q["id"],
            question=q["question"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            difficulty=q["difficulty"]
        ) for q in practice_questions
    ]

    return TestResponse(
        id=new_id,
        user_id=current_user["id"],
        title=title,
        youtube_urls=[],
        question_count=len(public_q),
        difficulty="mixed",
        questions=public_q,
        created_at=practice_doc["created_at"]
    )
