"""
AI FOR EDUCATION – Podcast API Routes
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.podcast_service import create_podcast

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/podcast", tags=["AI Podcast"])


class PodcastRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200, description="Podcast topic")
    language: str = Field(default="en", description="Language code")
    length: str = Field(default="medium", description="Length (short, medium, long)")

class PodcastResponse(BaseModel):
    topic: str
    script: list[dict]
    audio_url: str
    language: str
    length: str

@router.post("/generate", response_model=PodcastResponse)
def generate_podcast(req: PodcastRequest):
    """
    Generate an AI podcast on the given topic in the specified language and length.
    Returns the script and audio URL.
    """
    try:
        result = create_podcast(req.topic, req.language, req.length)
        return PodcastResponse(
            topic=result["topic"],
            script=result["script"],
            audio_url=result["audio_url"],
            language=req.language,
            length=req.length,
        )
    except Exception as e:
        logger.error(f"[Podcast] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Podcast generation failed: {str(e)}")
