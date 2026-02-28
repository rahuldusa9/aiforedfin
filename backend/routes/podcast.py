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


class PodcastResponse(BaseModel):
    topic: str
    script: list[dict]
    audio_url: str


@router.post("/generate", response_model=PodcastResponse)
def generate_podcast(req: PodcastRequest):
    """
    Generate an AI podcast on the given topic.
    Returns the script and audio URL.
    """
    try:
        result = create_podcast(req.topic)
        return PodcastResponse(
            topic=result["topic"],
            script=result["script"],
            audio_url=result["audio_url"],
        )
    except Exception as e:
        logger.error(f"[Podcast] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Podcast generation failed: {str(e)}")
