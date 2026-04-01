"""
AI FOR EDUCATION – Voice Learning Routes
Voice commands and oral practice.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.voice_service import get_voice_service

router = APIRouter(prefix="/api/voice", tags=["voice"])


class VoiceInputRequest(BaseModel):
    text: str
    language: Optional[str] = "en"


class OralPracticeRequest(BaseModel):
    topic: str
    practice_type: Optional[str] = "vocabulary"
    language: Optional[str] = "en"
    difficulty: Optional[str] = "medium"


class PronunciationCheckRequest(BaseModel):
    expected: str
    spoken: str
    language: Optional[str] = "en"


@router.post("/process/{user_id}")
async def process_voice_input(user_id: str, request: VoiceInputRequest):
    """Process voice input and return appropriate action."""
    service = get_voice_service()
    result = await service.process_voice_input(
        text=request.text,
        user_id=user_id,
        language=request.language
    )
    return result


@router.post("/parse")
async def parse_voice_command(request: VoiceInputRequest):
    """Parse a voice command without processing."""
    service = get_voice_service()
    command_type, params = service.parse_voice_command(request.text)
    return {
        "command": command_type,
        "params": params,
        "recognized": command_type is not None
    }


@router.post("/oral-practice")
async def generate_oral_practice(request: OralPracticeRequest):
    """Generate oral practice exercises."""
    service = get_voice_service()
    result = await service.generate_oral_practice(
        topic=request.topic,
        practice_type=request.practice_type,
        language=request.language,
        difficulty=request.difficulty
    )
    return result


@router.post("/pronunciation-check")
async def check_pronunciation(request: PronunciationCheckRequest):
    """Check pronunciation accuracy."""
    service = get_voice_service()
    result = await service.check_pronunciation(
        expected_text=request.expected,
        spoken_text=request.spoken,
        language=request.language
    )
    return result


@router.get("/tips")
async def get_voice_tips(language: str = "en"):
    """Get tips for voice learning."""
    service = get_voice_service()
    tips = service.get_voice_tips(language)
    return {"tips": tips}


@router.get("/commands")
async def get_available_commands():
    """Get list of available voice commands."""
    return {
        "commands": [
            {"phrase": "Tell me a story about [topic]", "action": "Generate a story"},
            {"phrase": "Quiz me on [topic]", "action": "Start a quiz"},
            {"phrase": "Create flashcards about [topic]", "action": "Generate flashcards"},
            {"phrase": "Review my flashcards", "action": "Start flashcard review"},
            {"phrase": "Explain [concept]", "action": "Get an explanation"},
            {"phrase": "Take notes on [topic]", "action": "Generate study notes"},
            {"phrase": "Practice [topic]", "action": "Get practice exercises"},
            {"phrase": "Go to [page]", "action": "Navigate to page"},
            {"phrase": "Help", "action": "Show available commands"},
        ]
    }
