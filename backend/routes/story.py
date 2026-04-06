"""
AI FOR EDUCATION – Story API Routes
Multilingual story generation with prosody-enhanced narration.
Supports 25+ languages with expressive TTS.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services.story_service import create_story
from services.multilingual_story_engine import (
    generate_multilingual_story, get_supported_languages,
    get_story_engine, StoryGenre, AgeGroup
)
from services.tts_service import (
    generate_multilingual_story_audio, list_supported_languages,
    get_available_voices_for_language
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/story", tags=["AI Storytelling"])


# -------------------------------------------------------
# Request/Response Models
# -------------------------------------------------------

class StoryRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200, description="Story topic")
    word_count: int = Field(default=400, ge=300, le=1000, description="Approximate word count")

class StoryResponse(BaseModel):
    topic: str
    story_text: str
    audio_url: str

class MultilingualStoryRequest(BaseModel):
    """Request for multilingual story generation."""
    topic: str = Field(..., min_length=2, max_length=200, description="Educational topic")
    language: str = Field(default="en", description="Language code (en, es, fr, de, zh, ja, ko, etc.)")
    genre: str = Field(default="educational", description="Story genre")
    age_group: str = Field(default="kids", description="Target age (children, kids, teens, adults)")
    word_count: int = Field(default=400, ge=300, le=1000, description="Approximate word count (300-1000)")
    include_audio: bool = Field(default=True, description="Generate audio narration")
    include_prosody: bool = Field(default=True, description="Apply expressive prosody")


class MultilingualStoryResponse(BaseModel):
    """Response with multilingual story and metadata."""
    topic: str
    story_text: str
    language: str
    language_name: str
    genre: str
    age_group: str
    word_count: int
    voice: str
    has_prosody: bool
    audio_url: Optional[str] = None
    prosody: Optional[dict] = None


class LanguageInfo(BaseModel):
    """Information about a supported language."""
    code: str
    name: str
    voice_count: int


class VoiceInfo(BaseModel):
    """Information about a voice."""
    id: str
    gender: str
    style: str
    description: str
    language_code: Optional[str] = None


# -------------------------------------------------------
# Basic Story Endpoint (Backward Compatible)
# -------------------------------------------------------

@router.post("/generate", response_model=StoryResponse)
def generate_story_endpoint(req: StoryRequest):
    """Generate an educational story with audio narration (English)."""
    try:
        result = create_story(req.topic, req.word_count)
        return StoryResponse(**result)
    except Exception as e:
        logger.error(f"[Story] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")


# -------------------------------------------------------
# Multilingual Story Endpoints
# -------------------------------------------------------

@router.post("/multilingual", response_model=MultilingualStoryResponse)
def generate_multilingual_story_endpoint(req: MultilingualStoryRequest):
    """
    Generate an educational story in any supported language.

    Features:
    - 25+ languages supported
    - Multiple genres (adventure, mystery, science, fantasy, etc.)
    - Age-appropriate content (children, kids, teens, adults)
    - Prosody-enhanced narration for expressive speech
    - Language-native voices
    """
    try:
        # Generate the story
        story_data = generate_multilingual_story(
            topic=req.topic,
            language=req.language,
            genre=req.genre,
            age_group=req.age_group,
            word_count=req.word_count,
            include_prosody=req.include_prosody
        )

        audio_url = None
        if req.include_audio:
            # Generate audio with multilingual TTS
            audio_path = generate_multilingual_story_audio(story_data)
            audio_filename = audio_path.split("/")[-1].split("\\")[-1]
            audio_url = f"/audio/{audio_filename}"
            logger.info(f"[Story] Audio generated: {audio_url}")

        return MultilingualStoryResponse(
            topic=story_data["topic"],
            story_text=story_data["story_text"],
            language=story_data["language"],
            language_name=story_data["language_name"],
            genre=story_data["genre"],
            age_group=story_data["age_group"],
            word_count=story_data["word_count"],
            voice=story_data["voice"],
            has_prosody=story_data["has_prosody"],
            audio_url=audio_url,
            prosody=story_data.get("prosody")
        )

    except Exception as e:
        logger.error(f"[Story] Multilingual generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Multilingual story generation failed: {str(e)}"
        )


@router.get("/languages", response_model=List[LanguageInfo])
def get_languages():
    """
    Get list of all supported languages for story generation.

    Returns languages with their codes, names, and available voice counts.
    """
    try:
        languages = get_supported_languages()
        return [
            LanguageInfo(
                code=lang["code"],
                name=lang["name"],
                voice_count=lang["voice_count"]
            )
            for lang in languages
        ]
    except Exception as e:
        logger.error(f"[Story] Error fetching languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices/{language}", response_model=List[VoiceInfo])
def get_voices_for_language_endpoint(language: str):
    """
    Get available voices for a specific language.

    Args:
        language: Language code (e.g., 'en', 'es', 'fr')

    Returns:
        List of available voices with gender, style, and description
    """
    try:
        voices = get_available_voices_for_language(language)
        if not voices:
            raise HTTPException(
                status_code=404,
                detail=f"No voices found for language: {language}"
            )
        return [VoiceInfo(**v) for v in voices]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Story] Error fetching voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/genres")
def get_genres():
    """Get list of available story genres."""
    return {
        "genres": [
            {"id": "adventure", "name": "Adventure", "description": "Exciting journeys and exploration"},
            {"id": "mystery", "name": "Mystery", "description": "Puzzles and detective stories"},
            {"id": "science", "name": "Science Fiction", "description": "Scientific concepts in futuristic settings"},
            {"id": "history", "name": "Historical", "description": "Stories set in historical periods"},
            {"id": "fantasy", "name": "Fantasy", "description": "Magical worlds and creatures"},
            {"id": "biography", "name": "Biography", "description": "Stories about real people"},
            {"id": "fable", "name": "Fable", "description": "Moral stories with lessons"},
            {"id": "educational", "name": "Educational", "description": "Direct educational narratives"},
        ]
    }


@router.get("/age-groups")
def get_age_groups():
    """Get list of available age groups."""
    return {
        "age_groups": [
            {"id": "children", "name": "Children", "ages": "5-8", "description": "Simple vocabulary, short sentences"},
            {"id": "kids", "name": "Kids", "ages": "9-12", "description": "Moderate vocabulary, engaging plots"},
            {"id": "teens", "name": "Teens", "ages": "13-17", "description": "Advanced vocabulary, complex themes"},
            {"id": "adults", "name": "Adults", "ages": "18+", "description": "Sophisticated language, nuanced content"},
        ]
    }


# -------------------------------------------------------
# Batch/Multi-Language Generation
# -------------------------------------------------------

class BatchStoryRequest(BaseModel):
    """Request to generate same story in multiple languages."""
    topic: str = Field(..., min_length=2, max_length=200)
    languages: List[str] = Field(..., min_items=1, max_items=5)
    genre: str = Field(default="educational")
    age_group: str = Field(default="kids")
    word_count: int = Field(default=400, ge=300, le=800)
    include_audio: bool = Field(default=False)


@router.post("/batch")
def generate_batch_stories(req: BatchStoryRequest):
    """
    Generate the same story in multiple languages.

    Useful for multilingual educational content.
    Limited to 5 languages per request.
    """
    try:
        engine = get_story_engine()
        results = []

        for lang in req.languages:
            try:
                story_data = generate_multilingual_story(
                    topic=req.topic,
                    language=lang,
                    genre=req.genre,
                    age_group=req.age_group,
                    word_count=req.word_count,
                    include_prosody=True
                )

                audio_url = None
                if req.include_audio:
                    audio_path = generate_multilingual_story_audio(story_data)
                    audio_filename = audio_path.split("/")[-1].split("\\")[-1]
                    audio_url = f"/audio/{audio_filename}"

                results.append({
                    "language": story_data["language"],
                    "language_name": story_data["language_name"],
                    "story_text": story_data["story_text"],
                    "word_count": story_data["word_count"],
                    "audio_url": audio_url,
                    "success": True
                })

            except Exception as e:
                logger.error(f"[Story] Batch generation failed for {lang}: {e}")
                results.append({
                    "language": lang,
                    "success": False,
                    "error": str(e)
                })

        return {
            "topic": req.topic,
            "total_languages": len(req.languages),
            "successful": sum(1 for r in results if r.get("success")),
            "stories": results
        }

    except Exception as e:
        logger.error(f"[Story] Batch generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
