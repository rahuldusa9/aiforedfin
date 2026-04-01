"""
AI FOR EDUCATION – Emotional Log Model
MongoDB document schema for emotional_logs collection.
"""

from datetime import datetime, timezone


COLLECTION = "emotional_logs"


def create_emotional_log_doc(
    user_id: str,
    message: str,
    detected_sentiment: str,
    confidence: float = None,
    ai_response: str = None,
    supportive_mode: bool = False,
) -> dict:
    """Build an emotional log document for insertion."""
    return {
        "user_id": user_id,
        "message": message,
        "detected_sentiment": detected_sentiment,
        "confidence": confidence,
        "ai_response": ai_response,
        "supportive_mode": supportive_mode,
        "created_at": datetime.now(timezone.utc),
    }


def emotional_log_to_response(doc: dict) -> dict:
    """Convert a MongoDB emotional log document to API response format."""
    return {
        "id": str(doc["_id"]),
        "message": doc["message"],
        "detected_sentiment": doc["detected_sentiment"],
        "confidence": doc.get("confidence"),
        "ai_response": doc.get("ai_response"),
        "supportive_mode": bool(doc.get("supportive_mode", False)),
        "created_at": str(doc.get("created_at", "")),
    }
