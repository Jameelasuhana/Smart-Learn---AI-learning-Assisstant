import re

def clean_transcript(text: str) -> str:
    """Clean and normalize raw video transcripts."""
    if not text:
        return ""
    
    # Remove HTML tags if any
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Replace multiple newlines or spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove recurring automated YouTube subtitle tags like [Music], [Applause], [Laughter]
    text = re.sub(r'\[(Music|Applause|Laughter|Silence|Noise|Background Music)\]', '', text, flags=re.IGNORECASE)
    
    # Trim leading/trailing whitespace
    cleaned = text.strip()
    return cleaned

def extract_youtube_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    url = url.strip()
    # Patterns for standard, short, embed, or query param URLs
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/|v\/|youtu\.be\/|watch\?v=)([^#\&\?]*).*'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            v_id = match.group(1)
            if len(v_id) == 11:
                return v_id
    # If the input itself is an 11-char ID
    if len(url) == 11 and re.match(r'^[0-9A-Za-z_-]{11}$', url):
        return url
    return ""
