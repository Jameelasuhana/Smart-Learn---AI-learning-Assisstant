from typing import List
from pydantic import BaseModel, Field

class TranscriptRequest(BaseModel):
    urls: List[str] = Field(..., min_items=1, description="List of public YouTube URLs")

class VideoTranscriptDetail(BaseModel):
    url: str
    video_id: str
    transcript_length: int
    success: bool
    error_message: str = ""

class TranscriptResponse(BaseModel):
    combined_transcript: str
    total_videos: int
    successful_videos: int
    video_details: List[VideoTranscriptDetail]
