"""
AI FOR EDUCATION – Flashcard Models
Flashcards with SM-2 Spaced Repetition Algorithm
"""

from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
import math


class CardDifficulty(str, Enum):
    """User rating of card difficulty."""
    AGAIN = "again"      # Complete blackout, reset
    HARD = "hard"        # Remembered with difficulty
    GOOD = "good"        # Remembered correctly
    EASY = "easy"        # Too easy


class CardStatus(str, Enum):
    """Card learning status."""
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    MASTERED = "mastered"


# SM-2 Algorithm Constants
SM2_MIN_EASINESS = 1.3
SM2_DEFAULT_EASINESS = 2.5
SM2_INITIAL_INTERVAL = 1  # days


def calculate_sm2(
    quality: int,  # 0-5 rating (0-1: again, 2: hard, 3: good, 4-5: easy)
    repetitions: int,
    easiness_factor: float,
    interval: int
) -> tuple:
    """
    SM-2 Spaced Repetition Algorithm.

    Returns: (new_repetitions, new_easiness_factor, new_interval_days)
    """
    # Quality < 3 means incorrect response
    if quality < 3:
        # Reset repetitions, keep easiness
        return (0, easiness_factor, 1)

    # Correct response
    new_repetitions = repetitions + 1

    # Update easiness factor
    new_ef = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ef = max(SM2_MIN_EASINESS, new_ef)

    # Calculate new interval
    if new_repetitions == 1:
        new_interval = 1
    elif new_repetitions == 2:
        new_interval = 6
    else:
        new_interval = int(interval * new_ef)

    return (new_repetitions, new_ef, new_interval)


def difficulty_to_quality(difficulty: CardDifficulty) -> int:
    """Convert difficulty rating to SM-2 quality score."""
    mapping = {
        CardDifficulty.AGAIN: 1,
        CardDifficulty.HARD: 2,
        CardDifficulty.GOOD: 3,
        CardDifficulty.EASY: 5,
    }
    return mapping.get(difficulty, 3)


def flashcard_schema() -> dict:
    """Schema for a single flashcard."""
    return {
        "card_id": str,
        "deck_id": str,
        "user_id": str,

        # Card content
        "front": str,           # Question/term
        "back": str,            # Answer/definition
        "hint": str,            # Optional hint
        "example": str,         # Optional example
        "image_url": str,       # Optional image
        "audio_url": str,       # Optional audio
        "tags": [],             # Topic tags

        # SM-2 Algorithm data
        "repetitions": 0,
        "easiness_factor": SM2_DEFAULT_EASINESS,
        "interval": SM2_INITIAL_INTERVAL,
        "next_review": datetime.utcnow(),
        "last_reviewed": None,

        # Statistics
        "status": CardStatus.NEW.value,
        "times_reviewed": 0,
        "times_correct": 0,
        "times_incorrect": 0,
        "average_time_ms": 0,

        # Metadata
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": "user",  # "user" or "ai"
    }


def deck_schema() -> dict:
    """Schema for a flashcard deck."""
    return {
        "deck_id": str,
        "user_id": str,

        # Deck info
        "name": str,
        "description": str,
        "topic": str,
        "language": "en",
        "is_public": False,
        "cover_image": str,

        # Statistics
        "card_count": 0,
        "cards_new": 0,
        "cards_learning": 0,
        "cards_review": 0,
        "cards_mastered": 0,

        # Learning progress
        "total_reviews": 0,
        "average_accuracy": 0.0,
        "last_studied": None,
        "study_streak": 0,

        # Metadata
        "tags": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def review_session_schema() -> dict:
    """Schema for a review session."""
    return {
        "session_id": str,
        "user_id": str,
        "deck_id": str,

        # Session data
        "started_at": datetime.utcnow(),
        "ended_at": None,
        "cards_reviewed": 0,
        "cards_correct": 0,
        "cards_incorrect": 0,

        # Performance
        "accuracy": 0.0,
        "average_time_per_card_ms": 0,
        "total_time_ms": 0,

        # Cards reviewed in this session
        "card_results": [],  # [{card_id, difficulty, time_ms, correct}]
    }


class FlashcardEngine:
    """Engine for managing flashcard reviews with SM-2 algorithm."""

    @staticmethod
    def process_review(
        card: dict,
        difficulty: CardDifficulty,
        time_ms: int = 0
    ) -> dict:
        """
        Process a card review and update SM-2 parameters.

        Returns updated card data.
        """
        quality = difficulty_to_quality(difficulty)

        # Get current SM-2 values
        repetitions = card.get("repetitions", 0)
        easiness_factor = card.get("easiness_factor", SM2_DEFAULT_EASINESS)
        interval = card.get("interval", SM2_INITIAL_INTERVAL)

        # Calculate new values
        new_reps, new_ef, new_interval = calculate_sm2(
            quality, repetitions, easiness_factor, interval
        )

        # Update card data
        now = datetime.utcnow()
        is_correct = quality >= 3

        # Update statistics
        times_reviewed = card.get("times_reviewed", 0) + 1
        times_correct = card.get("times_correct", 0) + (1 if is_correct else 0)
        times_incorrect = card.get("times_incorrect", 0) + (0 if is_correct else 1)

        # Calculate new average time
        old_avg = card.get("average_time_ms", 0)
        if old_avg > 0 and time_ms > 0:
            new_avg = (old_avg * (times_reviewed - 1) + time_ms) / times_reviewed
        else:
            new_avg = time_ms if time_ms > 0 else old_avg

        # Determine status
        if new_reps == 0:
            status = CardStatus.LEARNING.value
        elif new_interval >= 21:  # 3 weeks
            status = CardStatus.MASTERED.value
        elif new_reps >= 2:
            status = CardStatus.REVIEW.value
        else:
            status = CardStatus.LEARNING.value

        return {
            "repetitions": new_reps,
            "easiness_factor": new_ef,
            "interval": new_interval,
            "next_review": now + timedelta(days=new_interval),
            "last_reviewed": now,
            "status": status,
            "times_reviewed": times_reviewed,
            "times_correct": times_correct,
            "times_incorrect": times_incorrect,
            "average_time_ms": int(new_avg),
            "updated_at": now,
        }

    @staticmethod
    def get_cards_due(cards: List[dict], limit: int = 20) -> List[dict]:
        """
        Get cards due for review, prioritized by:
        1. Overdue cards (sorted by how overdue)
        2. New cards
        3. Cards due today
        """
        now = datetime.utcnow()

        overdue = []
        due_today = []
        new_cards = []

        for card in cards:
            next_review = card.get("next_review")
            status = card.get("status", CardStatus.NEW.value)

            if status == CardStatus.NEW.value:
                new_cards.append(card)
            elif next_review:
                if isinstance(next_review, str):
                    next_review = datetime.fromisoformat(next_review)

                if next_review <= now:
                    days_overdue = (now - next_review).days
                    card["_overdue_days"] = days_overdue
                    overdue.append(card)
                elif next_review.date() == now.date():
                    due_today.append(card)

        # Sort overdue by most overdue first
        overdue.sort(key=lambda x: x.get("_overdue_days", 0), reverse=True)

        # Combine: overdue first, then new cards, then due today
        result = overdue + new_cards + due_today

        # Clean up temporary field
        for card in result:
            card.pop("_overdue_days", None)

        return result[:limit]

    @staticmethod
    def calculate_deck_stats(cards: List[dict]) -> dict:
        """Calculate statistics for a deck."""
        total = len(cards)
        if total == 0:
            return {
                "total": 0,
                "new": 0,
                "learning": 0,
                "review": 0,
                "mastered": 0,
                "due_today": 0,
                "overdue": 0,
                "accuracy": 0,
            }

        now = datetime.utcnow()

        stats = {
            "total": total,
            "new": 0,
            "learning": 0,
            "review": 0,
            "mastered": 0,
            "due_today": 0,
            "overdue": 0,
        }

        total_correct = 0
        total_reviewed = 0

        for card in cards:
            status = card.get("status", CardStatus.NEW.value)
            stats[status] = stats.get(status, 0) + 1

            # Check if due
            next_review = card.get("next_review")
            if next_review:
                if isinstance(next_review, str):
                    next_review = datetime.fromisoformat(next_review)

                if next_review <= now:
                    if next_review.date() < now.date():
                        stats["overdue"] += 1
                    else:
                        stats["due_today"] += 1

            # Accuracy stats
            reviewed = card.get("times_reviewed", 0)
            correct = card.get("times_correct", 0)
            total_reviewed += reviewed
            total_correct += correct

        stats["accuracy"] = (total_correct / total_reviewed * 100) if total_reviewed > 0 else 0

        return stats


def create_flashcard(
    user_id: str,
    deck_id: str,
    front: str,
    back: str,
    hint: str = "",
    example: str = "",
    tags: list = None,
    created_by: str = "user"
) -> dict:
    """Create a new flashcard."""
    import uuid

    card = flashcard_schema()
    card["card_id"] = str(uuid.uuid4())
    card["deck_id"] = deck_id
    card["user_id"] = user_id
    card["front"] = front
    card["back"] = back
    card["hint"] = hint
    card["example"] = example
    card["tags"] = tags or []
    card["created_by"] = created_by
    card["next_review"] = datetime.utcnow()

    return card


def create_deck(
    user_id: str,
    name: str,
    description: str = "",
    topic: str = "",
    language: str = "en",
    is_public: bool = False
) -> dict:
    """Create a new flashcard deck."""
    import uuid

    deck = deck_schema()
    deck["deck_id"] = str(uuid.uuid4())
    deck["user_id"] = user_id
    deck["name"] = name
    deck["description"] = description
    deck["topic"] = topic
    deck["language"] = language
    deck["is_public"] = is_public

    return deck
