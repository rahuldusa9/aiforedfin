"""
AI FOR EDUCATION – Story API Routes
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.story_service import create_story

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/story", tags=["AI Storytelling"])


class StoryRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200, description="Story topic")


class StoryResponse(BaseModel):
    topic: str
    story_text: str
    audio_url: str


@router.post("/generate", response_model=StoryResponse)
def generate_story_endpoint(req: StoryRequest):
    """Generate an educational story with audio narration."""
    try:
        result = create_story(req.topic)
        return StoryResponse(**result)
    except Exception as e:
        logger.error(f"[Story] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")
