"""
AI FOR EDUCATION – Learning Progress Model
MongoDB document schema for learning_progress collection.
"""

from datetime import datetime, timezone


COLLECTION = "learning_progress"


def create_learning_progress_doc(
    user_id: str,
    module: str,
    topic: str,
    status: str = "in_progress",
    progress_percent: float = 0.0,
    notes: str = None,
    time_spent_seconds: float = 0.0,
) -> dict:
    """Build a learning progress document for insertion."""
    now = datetime.now(timezone.utc)
    return {
        "user_id": user_id,
        "module": module,
        "topic": topic,
        "status": status,
        "progress_percent": progress_percent,
        "notes": notes,
        "time_spent_seconds": time_spent_seconds,
        "created_at": now,
        "updated_at": now,
    }
