"""
AI FOR EDUCATION - Recommendation Service
Handles data retrieval and recommendation orchestration.
"""

import logging
from typing import Optional
from datetime import datetime, timezone, timedelta

from ml.recommendation_model import (
    recommend_topics,
    recommend_difficulty,
    recommend_content_type,
    get_comprehensive_recommendations
)

logger = logging.getLogger(__name__)


def get_user_recommendations(
    db,
    user_id: str,
    target_topic: Optional[str] = None,
    days_lookback: int = 30
) -> dict:
    """
    Fetch user data and generate comprehensive recommendations.

    Args:
        db: MongoDB database instance
        user_id: User ID to get recommendations for
        target_topic: Optional topic for context-aware recommendations
        days_lookback: Number of days of history to analyze

    Returns:
        Comprehensive recommendations dict
    """
    if not user_id or not user_id.strip():
        raise ValueError("User ID is required")

    # Calculate date cutoff
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_lookback)

    try:
        # Fetch quiz results
        quiz_results = list(db.quiz_results.find({
            "user_id": user_id,
            "created_at": {"$gte": cutoff_date}
        }).sort("created_at", -1).limit(100))

        # Fetch learning progress
        learning_progress = list(db.learning_progress.find({
            "user_id": user_id
        }).sort("updated_at", -1).limit(100))

        # Fetch emotional logs
        emotional_logs = list(db.emotional_logs.find({
            "user_id": user_id,
            "created_at": {"$gte": cutoff_date}
        }).sort("created_at", -1).limit(50))

        logger.info(
            f"[Recommendations] Fetched data for user {user_id}: "
            f"{len(quiz_results)} quizzes, {len(learning_progress)} progress, "
            f"{len(emotional_logs)} emotional logs"
        )

        # Generate recommendations
        recommendations = get_comprehensive_recommendations(
            quiz_results=quiz_results,
            learning_progress=learning_progress,
            emotional_logs=emotional_logs,
            target_topic=target_topic
        )

        recommendations["user_id"] = user_id
        recommendations["data_summary"] = {
            "quiz_results_count": len(quiz_results),
            "learning_progress_count": len(learning_progress),
            "emotional_logs_count": len(emotional_logs),
            "lookback_days": days_lookback
        }

        return recommendations

    except Exception as e:
        logger.error(f"[Recommendations] Error generating recommendations for {user_id}: {e}")
        raise


def get_topic_recommendations_only(
    db,
    user_id: str,
    limit: int = 5
) -> dict:
    """
    Get only topic recommendations.

    Args:
        db: MongoDB database instance
        user_id: User ID
        limit: Max number of recommendations

    Returns:
        Topic recommendations dict
    """
    if not user_id or not user_id.strip():
        raise ValueError("User ID is required")

    try:
        quiz_results = list(db.quiz_results.find({"user_id": user_id}).limit(100))
        learning_progress = list(db.learning_progress.find({"user_id": user_id}).limit(100))

        return recommend_topics(quiz_results, learning_progress, limit)

    except Exception as e:
        logger.error(f"[Recommendations] Topic recommendation error for {user_id}: {e}")
        raise


def get_difficulty_recommendation_only(
    db,
    user_id: str,
    topic: Optional[str] = None
) -> dict:
    """
    Get only difficulty recommendation.

    Args:
        db: MongoDB database instance
        user_id: User ID
        topic: Optional topic to filter by

    Returns:
        Difficulty recommendation dict
    """
    if not user_id or not user_id.strip():
        raise ValueError("User ID is required")

    try:
        quiz_results = list(db.quiz_results.find({"user_id": user_id}).limit(50))
        return recommend_difficulty(quiz_results, topic)

    except Exception as e:
        logger.error(f"[Recommendations] Difficulty recommendation error for {user_id}: {e}")
        raise


def get_content_recommendation_only(
    db,
    user_id: str,
    target_topic: Optional[str] = None
) -> dict:
    """
    Get only content type recommendation.

    Args:
        db: MongoDB database instance
        user_id: User ID
        target_topic: Optional topic for context

    Returns:
        Content type recommendation dict
    """
    if not user_id or not user_id.strip():
        raise ValueError("User ID is required")

    try:
        learning_progress = list(db.learning_progress.find({"user_id": user_id}).limit(100))
        emotional_logs = list(db.emotional_logs.find({"user_id": user_id}).limit(50))
        quiz_results = list(db.quiz_results.find({"user_id": user_id}).limit(50))

        return recommend_content_type(learning_progress, emotional_logs, target_topic, quiz_results)

    except Exception as e:
        logger.error(f"[Recommendations] Content recommendation error for {user_id}: {e}")
        raise
