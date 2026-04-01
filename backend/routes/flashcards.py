"""
AI FOR EDUCATION – Flashcard Routes
Flashcard management with spaced repetition.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from services.flashcard_service import get_flashcard_service
from models.flashcard import CardDifficulty

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


class CreateDeckRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    topic: Optional[str] = ""
    language: Optional[str] = "en"
    is_public: Optional[bool] = False


class AddCardRequest(BaseModel):
    front: str
    back: str
    hint: Optional[str] = ""
    example: Optional[str] = ""
    tags: Optional[List[str]] = None


class GenerateCardsRequest(BaseModel):
    topic: str
    count: Optional[int] = Field(default=10, ge=5, le=30)
    difficulty: Optional[str] = "medium"
    language: Optional[str] = "en"


class GenerateDeckRequest(BaseModel):
    topic: str
    card_count: Optional[int] = Field(default=15, ge=5, le=30)
    difficulty: Optional[str] = "medium"
    language: Optional[str] = "en"


class ReviewCardRequest(BaseModel):
    difficulty: str  # again, hard, good, easy
    time_ms: Optional[int] = 0


# ==================== DECK ROUTES ====================

@router.post("/decks/{user_id}")
async def create_deck(user_id: str, request: CreateDeckRequest):
    """Create a new flashcard deck."""
    service = get_flashcard_service()
    deck = await service.create_deck(
        user_id=user_id,
        name=request.name,
        description=request.description,
        topic=request.topic,
        language=request.language,
        is_public=request.is_public
    )
    return deck


@router.get("/decks/{user_id}")
async def get_user_decks(user_id: str):
    """Get all decks for a user."""
    service = get_flashcard_service()
    decks = await service.get_user_decks(user_id)
    return {"decks": decks}


@router.get("/deck/{deck_id}/{user_id}")
async def get_deck(deck_id: str, user_id: str):
    """Get a specific deck with cards."""
    service = get_flashcard_service()
    deck = await service.get_deck(deck_id, user_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck


@router.delete("/deck/{deck_id}/{user_id}")
async def delete_deck(deck_id: str, user_id: str):
    """Delete a deck and all its cards."""
    service = get_flashcard_service()
    success = await service.delete_deck(deck_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deck not found")
    return {"success": True}


# ==================== CARD ROUTES ====================

@router.post("/card/{deck_id}/{user_id}")
async def add_card(deck_id: str, user_id: str, request: AddCardRequest):
    """Add a card to a deck."""
    service = get_flashcard_service()
    card = await service.add_card(
        user_id=user_id,
        deck_id=deck_id,
        front=request.front,
        back=request.back,
        hint=request.hint,
        example=request.example,
        tags=request.tags
    )
    return card


@router.delete("/card/{card_id}/{user_id}")
async def delete_card(card_id: str, user_id: str):
    """Delete a card."""
    service = get_flashcard_service()
    success = await service.delete_card(card_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"success": True}


# ==================== REVIEW ROUTES ====================

@router.get("/review/{deck_id}/{user_id}")
async def get_cards_for_review(deck_id: str, user_id: str, limit: int = 20):
    """Get cards due for review."""
    service = get_flashcard_service()
    cards = await service.get_cards_for_review(deck_id, user_id, limit)
    return {"cards": cards, "count": len(cards)}


@router.post("/review/{card_id}/{user_id}")
async def review_card(card_id: str, user_id: str, request: ReviewCardRequest):
    """Process a card review."""
    service = get_flashcard_service()

    try:
        difficulty = CardDifficulty(request.difficulty)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid difficulty. Use: again, hard, good, easy")

    result = await service.review_card(
        card_id=card_id,
        user_id=user_id,
        difficulty=difficulty,
        time_ms=request.time_ms
    )
    return result


@router.get("/session/{deck_id}/{user_id}")
async def start_study_session(deck_id: str, user_id: str):
    """Start a study session."""
    service = get_flashcard_service()
    session = await service.start_study_session(user_id, deck_id)
    return session


# ==================== AI GENERATION ====================

@router.post("/generate/{deck_id}/{user_id}")
async def generate_flashcards(deck_id: str, user_id: str, request: GenerateCardsRequest):
    """Generate flashcards using AI."""
    service = get_flashcard_service()

    try:
        cards = await service.generate_flashcards(
            user_id=user_id,
            deck_id=deck_id,
            topic=request.topic,
            count=request.count,
            difficulty=request.difficulty,
            language=request.language
        )
        return {"cards": cards, "count": len(cards)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-deck/{user_id}")
async def generate_deck_from_topic(user_id: str, request: GenerateDeckRequest):
    """Generate a complete deck from a topic."""
    service = get_flashcard_service()

    try:
        deck = await service.generate_deck_from_topic(
            user_id=user_id,
            topic=request.topic,
            card_count=request.card_count,
            difficulty=request.difficulty,
            language=request.language
        )
        return deck
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STATS ====================

@router.get("/stats/{user_id}")
async def get_study_stats(user_id: str):
    """Get overall flashcard study statistics."""
    service = get_flashcard_service()
    stats = await service.get_study_stats(user_id)
    return stats
