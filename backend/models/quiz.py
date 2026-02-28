"""
AI FOR EDUCATION – Quiz Results Model
MongoDB document schema for quiz_results collection.
"""

from datetime import datetime, timezone


COLLECTION = "quiz_results"


def create_quiz_result_doc(
    user_id: str,
    topic: str,
    difficulty: str,
    total_questions: int,
    correct_answers: int,
    score: float,
    time_taken_seconds: float,
    average_response_time: float = None,
    number_of_attempts: int = 1,
    predicted_performance: str = None,
    recommended_difficulty: str = None,
    weakness_probability: float = None,
) -> dict:
    """Build a quiz result document for insertion."""
    return {
        "user_id": user_id,
        "topic": topic,
        "difficulty": difficulty,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score": score,
        "time_taken_seconds": time_taken_seconds,
        "average_response_time": average_response_time,
        "number_of_attempts": number_of_attempts,
        "predicted_performance": predicted_performance,
        "recommended_difficulty": recommended_difficulty,
        "weakness_probability": weakness_probability,
        "created_at": datetime.now(timezone.utc),
    }


def quiz_result_to_response(doc: dict) -> dict:
    """Convert a MongoDB quiz result document to API response format."""
    return {
        "id": str(doc["_id"]),
        "topic": doc["topic"],
        "difficulty": doc["difficulty"],
        "score": doc["score"],
        "total_questions": doc["total_questions"],
        "correct_answers": doc["correct_answers"],
        "time_taken_seconds": doc["time_taken_seconds"],
        "predicted_performance": doc.get("predicted_performance"),
        "recommended_difficulty": doc.get("recommended_difficulty"),
        "weakness_probability": doc.get("weakness_probability"),
        "created_at": str(doc.get("created_at", "")),
    }
