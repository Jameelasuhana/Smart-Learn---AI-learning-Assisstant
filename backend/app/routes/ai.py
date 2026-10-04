from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.ai_schemas import (
    QuestionRequest, QuestionResponse,
    ExplainRequest, ExplainResponse,
    SummarizeRequest, SummarizeResponse
)
from app.services.gemini_service import ask_ai_question, explain_concept, summarize_text
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/ai", tags=["AI Tools"])

@router.post("/question", response_model=QuestionResponse)
async def handle_question(
    req: QuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        res = await ask_ai_question(req.question)
        return QuestionResponse(**res)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Question processing failed: {str(e)}"
        )

@router.post("/explain", response_model=ExplainResponse)
async def handle_explain(
    req: ExplainRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        res = await explain_concept(req.concept, req.level)
        return ExplainResponse(**res)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Concept explanation failed: {str(e)}"
        )

@router.post("/summarize", response_model=SummarizeResponse)
async def handle_summarize(
    req: SummarizeRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        res = await summarize_text(req.text)
        return SummarizeResponse(**res)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summarization failed: {str(e)}"
        )
