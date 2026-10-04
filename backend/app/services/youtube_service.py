import re
import logging
from typing import List, Dict, Tuple

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

logger = logging.getLogger(__name__)


def extract_youtube_video_id(url: str) -> str:
    """
    Extracts the 11-character YouTube video ID from various YouTube URL formats.
    """

    if not url:
        return ""

    url = url.strip()

    # Standard patterns: watch?v=ID, youtu.be/ID, embed/ID, shorts/ID, v/ID
    patterns = [
        r'(?:v=|\/|vi\/|u\/\w\/|embed\/|shorts\/|e\/|v\/|watch\?.*v=)([^#&\?]*).*',
        r'youtu\.be\/([^#&\?]+)',
        r'youtube\.com\/watch\?v=([^#&\?]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            video_id = match.group(1)

            if len(video_id) == 11:
                return video_id

    # Direct 11-character string check
    if len(url) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url

    return ""


def get_transcript_for_video(url: str) -> Tuple[str, str, bool]:
    """
    Fetches public captions/transcript for a single YouTube video.

    Returns:
        (transcript_text, error_message, success_flag)
    """

    video_id = extract_youtube_video_id(url)

    if not video_id:
        return (
            "",
            "Invalid YouTube URL format. Please enter a valid YouTube video link.",
            False
        )

    try:
        # Create API client for youtube-transcript-api v1.2.4
        ytt_api = YouTubeTranscriptApi()

        # Fetch transcript using the new API
        transcript = ytt_api.fetch(
            video_id,
            languages=[
                "en",
                "en-US",
                "en-GB",
                "en-CA",
                "hi",
                "es",
                "fr",
                "de"
            ]
        )

        # Combine transcript text pieces
        pieces = [
            snippet.text.strip()
            for snippet in transcript
            if snippet.text
        ]

        clean_text = " ".join(pieces)

        # Clean repetitive music/sound tags like [Music], (applause), etc.
        clean_text = re.sub(r'\[.*?\]|\(.*?\)', '', clean_text)

        # Remove extra spaces
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        if len(clean_text) < 50:
            return (
                "",
                "The transcript extracted from this video is too short or empty.",
                False
            )

        return clean_text, "", True

    except (TranscriptsDisabled, NoTranscriptFound):
        return (
            "",
            "Subtitles/captions are disabled or unavailable for this video. "
            "Please try another video with captions enabled.",
            False
        )

    except VideoUnavailable:
        return (
            "",
            "This YouTube video is private or unavailable.",
            False
        )

    except Exception as e:
        logger.warning(
            f"Transcript extraction failed for video {video_id}: {str(e)}"
        )

        return (
            "",
            "Unable to extract a usable transcript from this video. "
            "Please try another video.",
            False
        )


def process_youtube_urls(urls: List[str]) -> Dict:
    """
    Processes multiple YouTube URLs, extracts transcripts, cleans them,
    and returns combined content along with status details for each URL.
    """

    clean_urls = [
        u.strip()
        for u in urls
        if u and u.strip()
    ]

    if not clean_urls:
        return {
            "combined_transcript": "",
            "total_videos": 0,
            "successful_videos": 0,
            "video_details": []
        }

    combined_texts = []
    details = []
    success_count = 0

    for index, url in enumerate(clean_urls, 1):

        video_id = extract_youtube_video_id(url)

        text, err, success = get_transcript_for_video(url)

        detail = {
            "url": url,
            "video_id": video_id or "unknown",
            "transcript_length": len(text),
            "success": success,
            "error_message": err
        }

        details.append(detail)

        if success:
            success_count += 1

            header = (
                f"\n--- VIDEO CONTENT {success_count} ({url}) ---\n"
            )

            combined_texts.append(header + text)

    combined_transcript = "\n".join(combined_texts).strip()

    return {
        "combined_transcript": combined_transcript,
        "total_videos": len(clean_urls),
        "successful_videos": success_count,
        "video_details": details
    }