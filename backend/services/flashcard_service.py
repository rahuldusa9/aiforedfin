"""
AI FOR EDUCATION – Flashcard Service
AI-powered flashcard generation with spaced repetition.
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from database import db
from models.flashcard import (
    FlashcardEngine, CardDifficulty, CardStatus,
    create_flashcard, create_deck, deck_schema
)
from services.gemini_service import generate_text

logger = logging.getLogger(__name__)


class FlashcardService:
    """Service for managing flashcards with AI generation."""

    def __init__(self):
        self.cards_collection = db.flashcards if db else None
        self.decks_collection = db.flashcard_decks if db else None

    def _get_cards_collection(self):
        if self.cards_collection is None:
            from database import db
            self.cards_collection = db.flashcards
        return self.cards_collection

    def _get_decks_collection(self):
        if self.decks_collection is None:
            from database import db
            self.decks_collection = db.flashcard_decks
        return self.decks_collection

    # ==================== DECK OPERATIONS ====================

    async def create_deck(
        self,
        user_id: str,
        name: str,
        description: str = "",
        topic: str = "",
        language: str = "en",
        is_public: bool = False
    ) -> dict:
        """Create a new flashcard deck."""
        decks = self._get_decks_collection()

        deck = create_deck(user_id, name, description, topic, language, is_public)
        decks.insert_one(deck)

        logger.info(f"[Flashcard] Created deck '{name}' for user {user_id}")

        return deck

    async def get_user_decks(self, user_id: str) -> List[dict]:
        """Get all decks for a user."""
        decks = self._get_decks_collection()
        cards = self._get_cards_collection()

        user_decks = list(decks.find({"user_id": user_id}))

        # Add card stats to each deck
        for deck in user_decks:
            deck_cards = list(cards.find({"deck_id": deck["deck_id"]}))
            stats = FlashcardEngine.calculate_deck_stats(deck_cards)
            deck["stats"] = stats
            deck["_id"] = str(deck["_id"])

        return user_decks

    async def get_deck(self, deck_id: str, user_id: str) -> Optional[dict]:
        """Get a specific deck."""
        decks = self._get_decks_collection()
        cards = self._get_cards_collection()

        deck = decks.find_one({"deck_id": deck_id, "user_id": user_id})
        if not deck:
            return None

        deck_cards = list(cards.find({"deck_id": deck_id}))
        deck["stats"] = FlashcardEngine.calculate_deck_stats(deck_cards)
        deck["cards"] = deck_cards
        deck["_id"] = str(deck["_id"])

        return deck

    async def delete_deck(self, deck_id: str, user_id: str) -> bool:
        """Delete a deck and all its cards."""
        decks = self._get_decks_collection()
        cards = self._get_cards_collection()

        result = decks.delete_one({"deck_id": deck_id, "user_id": user_id})
        if result.deleted_count > 0:
            cards.delete_many({"deck_id": deck_id})
            logger.info(f"[Flashcard] Deleted deck {deck_id}")
            return True
        return False

    # ==================== CARD OPERATIONS ====================

    async def add_card(
        self,
        user_id: str,
        deck_id: str,
        front: str,
        back: str,
        hint: str = "",
        example: str = "",
        tags: list = None
    ) -> dict:
        """Add a card to a deck."""
        cards = self._get_cards_collection()
        decks = self._get_decks_collection()

        card = create_flashcard(user_id, deck_id, front, back, hint, example, tags)
        cards.insert_one(card)

        # Update deck card count
        decks.update_one(
            {"deck_id": deck_id},
            {
                "$inc": {"card_count": 1, "cards_new": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        logger.info(f"[Flashcard] Added card to deck {deck_id}")

        return card

    async def get_cards_for_review(self, deck_id: str, user_id: str, limit: int = 20) -> List[dict]:
        """Get cards due for review."""
        cards = self._get_cards_collection()

        deck_cards = list(cards.find({"deck_id": deck_id, "user_id": user_id}))
        due_cards = FlashcardEngine.get_cards_due(deck_cards, limit)

        # Clean MongoDB _id
        for card in due_cards:
            card["_id"] = str(card["_id"])

        return due_cards

    async def review_card(
        self,
        card_id: str,
        user_id: str,
        difficulty: CardDifficulty,
        time_ms: int = 0
    ) -> dict:
        """Process a card review."""
        cards = self._get_cards_collection()
        decks = self._get_decks_collection()

        card = cards.find_one({"card_id": card_id, "user_id": user_id})
        if not card:
            raise ValueError(f"Card {card_id} not found")

        old_status = card.get("status", CardStatus.NEW.value)

        # Process review with SM-2
        updates = FlashcardEngine.process_review(card, difficulty, time_ms)

        # Update card
        cards.update_one({"card_id": card_id}, {"$set": updates})

        # Update deck stats if status changed
        new_status = updates["status"]
        if old_status != new_status:
            decks.update_one(
                {"deck_id": card["deck_id"]},
                {
                    "$inc": {
                        f"cards_{old_status}": -1,
                        f"cards_{new_status}": 1,
                        "total_reviews": 1,
                    },
                    "$set": {"last_studied": datetime.utcnow()}
                }
            )
        else:
            decks.update_one(
                {"deck_id": card["deck_id"]},
                {
                    "$inc": {"total_reviews": 1},
                    "$set": {"last_studied": datetime.utcnow()}
                }
            )

        logger.info(f"[Flashcard] Reviewed card {card_id}: {difficulty.value}")

        return {
            "card_id": card_id,
            "difficulty": difficulty.value,
            "new_status": new_status,
            "next_review": updates["next_review"].isoformat(),
            "interval_days": updates["interval"],
        }

    async def delete_card(self, card_id: str, user_id: str) -> bool:
        """Delete a card."""
        cards = self._get_cards_collection()
        decks = self._get_decks_collection()

        card = cards.find_one({"card_id": card_id, "user_id": user_id})
        if not card:
            return False

        status = card.get("status", CardStatus.NEW.value)

        result = cards.delete_one({"card_id": card_id})
        if result.deleted_count > 0:
            decks.update_one(
                {"deck_id": card["deck_id"]},
                {"$inc": {"card_count": -1, f"cards_{status}": -1}}
            )
            return True
        return False

    # ==================== AI GENERATION ====================

    async def generate_flashcards(
        self,
        user_id: str,
        deck_id: str,
        topic: str,
        count: int = 10,
        difficulty: str = "medium",
        language: str = "en"
    ) -> List[dict]:
        """Generate flashcards using AI."""

        prompt = f"""Generate {count} flashcards about "{topic}" for learning.

Difficulty level: {difficulty}
Language: {language}

Return a JSON array with this exact format:
[
  {{
    "front": "Question or term",
    "back": "Answer or definition",
    "hint": "Optional hint to help remember",
    "example": "Example usage or context"
  }}
]

Requirements:
- Make questions clear and specific
- Answers should be concise but complete
- Include helpful hints
- Provide real-world examples
- Vary question types (definitions, applications, comparisons)
- Difficulty should match: {difficulty}

Return ONLY the JSON array, no other text."""

        try:
            response = generate_text(prompt, max_tokens=3000)

            # Parse JSON from response
            # Find JSON array in response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON array found in response")

            json_str = response[start:end]
            flashcards_data = json.loads(json_str)

            # Create cards
            created_cards = []
            for card_data in flashcards_data:
                card = await self.add_card(
                    user_id=user_id,
                    deck_id=deck_id,
                    front=card_data.get("front", ""),
                    back=card_data.get("back", ""),
                    hint=card_data.get("hint", ""),
                    example=card_data.get("example", ""),
                    tags=[topic]
                )
                card["_id"] = str(card["_id"]) if "_id" in card else None
                created_cards.append(card)

            logger.info(f"[Flashcard] Generated {len(created_cards)} cards for topic '{topic}'")

            return created_cards

        except Exception as e:
            logger.error(f"[Flashcard] AI generation failed: {e}")
            raise RuntimeError(f"Failed to generate flashcards: {e}")

    async def generate_deck_from_topic(
        self,
        user_id: str,
        topic: str,
        card_count: int = 15,
        difficulty: str = "medium",
        language: str = "en"
    ) -> dict:
        """Generate a complete deck from a topic."""

        # Create deck
        deck = await self.create_deck(
            user_id=user_id,
            name=f"{topic} Flashcards",
            description=f"AI-generated flashcards about {topic}",
            topic=topic,
            language=language
        )

        # Generate cards
        cards = await self.generate_flashcards(
            user_id=user_id,
            deck_id=deck["deck_id"],
            topic=topic,
            count=card_count,
            difficulty=difficulty,
            language=language
        )

        deck["cards"] = cards
        deck["stats"] = FlashcardEngine.calculate_deck_stats(cards)

        return deck

    # ==================== STUDY SESSION ====================

    async def start_study_session(self, user_id: str, deck_id: str) -> dict:
        """Start a new study session."""
        session_id = str(uuid.uuid4())

        cards = await self.get_cards_for_review(deck_id, user_id)

        return {
            "session_id": session_id,
            "deck_id": deck_id,
            "cards_to_review": len(cards),
            "cards": cards,
            "started_at": datetime.utcnow().isoformat(),
        }

    async def get_study_stats(self, user_id: str) -> dict:
        """Get overall study statistics."""
        cards = self._get_cards_collection()
        decks = self._get_decks_collection()

        user_cards = list(cards.find({"user_id": user_id}))
        user_decks = list(decks.find({"user_id": user_id}))

        total_cards = len(user_cards)
        total_reviews = sum(c.get("times_reviewed", 0) for c in user_cards)
        total_correct = sum(c.get("times_correct", 0) for c in user_cards)

        now = datetime.utcnow()
        cards_due = sum(
            1 for c in user_cards
            if c.get("next_review") and c["next_review"] <= now
        )

        status_counts = {
            "new": 0,
            "learning": 0,
            "review": 0,
            "mastered": 0,
        }
        for card in user_cards:
            status = card.get("status", "new")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_decks": len(user_decks),
            "total_cards": total_cards,
            "cards_due": cards_due,
            "total_reviews": total_reviews,
            "accuracy": (total_correct / total_reviews * 100) if total_reviews > 0 else 0,
            "status_breakdown": status_counts,
            "mastery_rate": (status_counts["mastered"] / total_cards * 100) if total_cards > 0 else 0,
        }


# Global instance
_flashcard_service = None


def get_flashcard_service() -> FlashcardService:
    """Get or create the flashcard service instance."""
    global _flashcard_service
    if _flashcard_service is None:
        _flashcard_service = FlashcardService()
    return _flashcard_service
