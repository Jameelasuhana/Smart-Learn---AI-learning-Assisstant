from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.youtube_schemas import TranscriptRequest, TranscriptResponse
from app.services.youtube_service import process_youtube_urls
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/youtube", tags=["YouTube Transcript"])

@router.post("/transcript", response_model=TranscriptResponse)
async def extract_transcript(
    req: TranscriptRequest,
    current_user: dict = Depends(get_current_user)
):
    if not req.urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one YouTube URL must be provided."
        )
    
    result = process_youtube_urls(req.urls)
    
    if result["successful_videos"] == 0:
        first_err = result["video_details"][0]["error_message"] if result["video_details"] else "Transcript extraction failed."
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=first_err or "Unable to extract a usable transcript from the provided video(s). Please try another video."
        )

    return TranscriptResponse(**result)
