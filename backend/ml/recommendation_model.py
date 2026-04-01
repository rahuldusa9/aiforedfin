"""
AI FOR EDUCATION - Recommendation Engine
Multi-factor recommendation system for topics, difficulty, and content types.
"""

import pickle
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from collections import Counter

import numpy as np

logger = logging.getLogger(__name__)

ML_DIR = Path(__file__).parent
RECOMMENDATION_MODEL_PATH = ML_DIR / "recommendation_model.pkl"

# Cached model
_recommendation_model = None

# Constants
TOPICS = [
    "mathematics", "science", "history", "english",
    "programming", "geography", "physics", "chemistry",
    "biology", "literature"
]
DIFFICULTIES = ["easy", "medium", "hard"]
CONTENT_TYPES = ["quiz", "story", "podcast", "tutor"]
COLD_START_THRESHOLD = 3


def _load_recommendation_model():
    """Lazy singleton loader for recommendation model."""
    global _recommendation_model
    if _recommendation_model is not None:
        return

    if RECOMMENDATION_MODEL_PATH.exists():
        with open(RECOMMENDATION_MODEL_PATH, "rb") as f:
            _recommendation_model = pickle.load(f)
        logger.info("[ML] Recommendation model loaded.")
    else:
        # Initialize with default weights
        _recommendation_model = {
            "topic_weights": {
                "weakness": 0.35,
                "knowledge_gap": 0.30,
                "recency": 0.20,
                "completion_potential": 0.15
            },
            "difficulty_thresholds": {
                "increase": 80,
                "decrease": 50,
                "trend_sensitivity": 5
            },
            "content_weights": {
                "emotional_override": True,
                "familiarity_threshold": 0.3
            }
        }
        # Save default model
        with open(RECOMMENDATION_MODEL_PATH, "wb") as f:
            pickle.dump(_recommendation_model, f)
        logger.info("[ML] Recommendation model initialized with defaults.")


def recommend_topics(
    quiz_results: List[dict],
    learning_progress: List[dict],
    limit: int = 5
) -> dict:
    """
    Recommend topics based on weaknesses and knowledge gaps.

    Args:
        quiz_results: List of quiz result documents
        learning_progress: List of learning progress documents
        limit: Max number of recommendations

    Returns:
        {
            "recommendations": list[dict],
            "confidence": float,
            "data_points_used": int,
            "is_cold_start": bool
        }
    """
    _load_recommendation_model()

    # Cold start check
    if len(quiz_results) < COLD_START_THRESHOLD:
        return _cold_start_topics(limit)

    weights = _recommendation_model["topic_weights"]
    topic_scores = {}

    for topic in TOPICS:
        # Calculate weakness score
        topic_quizzes = [q for q in quiz_results if q.get("topic", "").lower() == topic]
        weakness_score = 0.0
        if topic_quizzes:
            weakness_probs = [q.get("weakness_probability", 0) for q in topic_quizzes]
            weakness_score = float(np.mean(weakness_probs))

        # Calculate knowledge gap
        topic_progress = [p for p in learning_progress if p.get("topic", "").lower() == topic]
        gap_score = 1.0  # Full gap if no progress
        if topic_progress:
            progress_pcts = [p.get("progress_percent", 0) for p in topic_progress]
            gap_score = 1.0 - (float(np.mean(progress_pcts)) / 100)

        # Calculate recency score
        recency_score = 0.0
        all_topic_records = topic_quizzes + topic_progress
        if all_topic_records:
            dates = []
            for r in all_topic_records:
                created = r.get("created_at")
                if created:
                    if isinstance(created, datetime):
                        dates.append(created)
            if dates:
                most_recent = max(dates)
                now = datetime.now(timezone.utc)
                if most_recent.tzinfo is None:
                    most_recent = most_recent.replace(tzinfo=timezone.utc)
                days_ago = (now - most_recent).days
                recency_score = min(days_ago / 30, 1.0)
        else:
            recency_score = 1.0  # Never studied

        # Completion potential
        completion_score = 0.0
        in_progress = [p for p in topic_progress if p.get("status") == "in_progress"]
        if in_progress:
            completion_score = min(0.5 + (len(in_progress) * 0.1), 1.0)

        # Combined score
        topic_scores[topic] = (
            weights["weakness"] * weakness_score +
            weights["knowledge_gap"] * gap_score +
            weights["recency"] * recency_score +
            weights["completion_potential"] * completion_score
        )

    # Sort and build recommendations
    sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)

    recommendations = []
    for topic, score in sorted_topics[:limit]:
        # Determine primary reason
        reason = "weakness_detected" if score > 0.6 else "knowledge_gap"
        if score > 0.7:
            reason = "high_priority"

        recommendations.append({
            "topic": topic,
            "priority": round(score, 3),
            "reason": reason,
            "weakness_probability": round(score * 0.5, 3),
        })

    # Confidence based on data volume
    data_points = len(quiz_results) + len(learning_progress)
    confidence = min(0.5 + (data_points / 50), 0.95)

    return {
        "recommendations": recommendations,
        "confidence": round(confidence, 3),
        "data_points_used": data_points,
        "is_cold_start": False
    }


def _cold_start_topics(limit: int) -> dict:
    """Return default topics for new users."""
    defaults = ["mathematics", "science", "english", "programming", "history"]
    return {
        "recommendations": [
            {"topic": t, "priority": 0.5, "reason": "starter_topic", "weakness_probability": 0.0}
            for t in defaults[:limit]
        ],
        "confidence": 0.5,
        "data_points_used": 0,
        "is_cold_start": True
    }


def recommend_difficulty(
    quiz_results: List[dict],
    topic: Optional[str] = None
) -> dict:
    """
    Recommend difficulty based on performance trends.

    Args:
        quiz_results: List of quiz result documents
        topic: Optional topic to filter by

    Returns:
        {
            "recommended_difficulty": str,
            "confidence": float,
            "reasoning": dict,
            "is_cold_start": bool
        }
    """
    _load_recommendation_model()

    # Filter by topic if specified
    if topic:
        quiz_results = [q for q in quiz_results if q.get("topic", "").lower() == topic.lower()]

    # Cold start check
    if len(quiz_results) < COLD_START_THRESHOLD:
        return _cold_start_difficulty()

    thresholds = _recommendation_model["difficulty_thresholds"]

    # Get recent scores (last 5)
    recent = sorted(
        quiz_results,
        key=lambda x: x.get("created_at", datetime.min),
        reverse=True
    )[:5]
    scores = [q.get("score", 50) for q in recent]

    # Calculate trend
    if len(scores) >= 2:
        trend_slope = (scores[0] - scores[-1]) / len(scores)
    else:
        trend_slope = 0

    avg_score = float(np.mean(scores))

    # Get current difficulty
    difficulties = [q.get("difficulty", "medium") for q in recent[:3]]
    current_difficulty = Counter(difficulties).most_common(1)[0][0]

    # Decision logic
    difficulty_order = ["easy", "medium", "hard"]
    try:
        current_idx = difficulty_order.index(current_difficulty)
    except ValueError:
        current_idx = 1  # Default to medium

    action = "maintain"
    if avg_score >= thresholds["increase"] and trend_slope >= 0:
        action = "increase"
        new_idx = min(current_idx + 1, 2)
    elif avg_score < thresholds["decrease"] or trend_slope < -thresholds["trend_sensitivity"]:
        action = "decrease"
        new_idx = max(current_idx - 1, 0)
    else:
        new_idx = current_idx

    recommended = difficulty_order[new_idx]

    # Confidence based on data consistency
    score_variance = float(np.var(scores)) if len(scores) > 1 else 50
    confidence = max(0.5, min(0.95, 1 - (score_variance / 1000)))

    return {
        "recommended_difficulty": recommended,
        "confidence": round(confidence, 3),
        "reasoning": {
            "average_score": round(avg_score, 1),
            "trend": "improving" if trend_slope > 0 else "declining" if trend_slope < 0 else "stable",
            "trend_slope": round(trend_slope, 2),
            "current_level": current_difficulty,
            "action": action
        },
        "is_cold_start": False
    }


def _cold_start_difficulty() -> dict:
    """Return default difficulty for new users."""
    return {
        "recommended_difficulty": "medium",
        "confidence": 0.5,
        "reasoning": {
            "average_score": None,
            "trend": "unknown",
            "trend_slope": None,
            "current_level": None,
            "action": "default"
        },
        "is_cold_start": True
    }


def recommend_content_type(
    learning_progress: List[dict],
    emotional_logs: List[dict],
    target_topic: Optional[str] = None,
    quiz_results: Optional[List[dict]] = None
) -> dict:
    """
    Recommend content type based on engagement and emotional state.

    Args:
        learning_progress: List of learning progress documents
        emotional_logs: List of emotional log documents
        target_topic: Optional topic for context
        quiz_results: Optional quiz results for familiarity calculation

    Returns:
        {
            "recommended_content": str,
            "confidence": float,
            "alternatives": list,
            "factors": dict,
            "is_cold_start": bool
        }
    """
    _load_recommendation_model()

    # Cold start check
    total_data = len(learning_progress) + len(emotional_logs)
    if total_data < COLD_START_THRESHOLD:
        return _cold_start_content()

    # Get dominant emotional state (last 5 entries)
    recent_emotions = sorted(
        emotional_logs,
        key=lambda x: x.get("created_at", datetime.min),
        reverse=True
    )[:5]

    emotional_state = "neutral"
    emotional_confidence = 0.5
    if recent_emotions:
        sentiments = [e.get("detected_sentiment", "neutral") for e in recent_emotions]
        emotional_state = Counter(sentiments).most_common(1)[0][0]
        emotional_confidence = float(np.mean([e.get("confidence", 0.5) for e in recent_emotions]))

    # Calculate engagement scores
    engagement = {"quiz": 0.25, "story": 0.25, "podcast": 0.25, "tutor": 0.25}
    total_time = sum(p.get("time_spent_seconds", 0) for p in learning_progress)

    if total_time > 0:
        for content_type in CONTENT_TYPES:
            type_records = [p for p in learning_progress if p.get("module", "").lower() == content_type]
            type_time = sum(p.get("time_spent_seconds", 0) for p in type_records)
            engagement[content_type] = type_time / total_time

    # Topic familiarity
    familiarity = 0.5
    if target_topic and quiz_results:
        topic_quizzes = [q for q in quiz_results if q.get("topic", "").lower() == target_topic.lower()]
        if topic_quizzes:
            avg_score = float(np.mean([q.get("score", 50) for q in topic_quizzes]))
            familiarity = avg_score / 100

    # Decision logic
    content_scores = {}

    # Emotional state override
    if emotional_state in ["stressed", "anxious"]:
        content_scores["story"] = 0.9
        content_scores["podcast"] = 0.85
        content_scores["quiz"] = 0.3
        content_scores["tutor"] = 0.5
    else:
        # Standard scoring
        content_scores["quiz"] = engagement["quiz"] * 0.6 + (1 - familiarity) * 0.4
        content_scores["story"] = engagement["story"] * 0.7 + 0.1
        content_scores["podcast"] = engagement["podcast"] * 0.6 + familiarity * 0.3
        content_scores["tutor"] = engagement["tutor"] * 0.5 + (1 - familiarity) * 0.3

    # Get recommendation
    sorted_content = sorted(content_scores.items(), key=lambda x: x[1], reverse=True)
    recommended = sorted_content[0][0]

    return {
        "recommended_content": recommended,
        "confidence": round(sorted_content[0][1], 3),
        "alternatives": [
            {"type": t, "score": round(s, 3)}
            for t, s in sorted_content[1:3]
        ],
        "factors": {
            "emotional_state": emotional_state,
            "emotional_confidence": round(emotional_confidence, 3),
            "topic_familiarity": round(familiarity, 3),
            "engagement_scores": {k: round(v, 3) for k, v in engagement.items()}
        },
        "is_cold_start": False
    }


def _cold_start_content() -> dict:
    """Return default content type for new users."""
    return {
        "recommended_content": "quiz",
        "confidence": 0.5,
        "alternatives": [
            {"type": "story", "score": 0.4},
            {"type": "podcast", "score": 0.35}
        ],
        "factors": {
            "emotional_state": "unknown",
            "emotional_confidence": 0.0,
            "topic_familiarity": 0.0,
            "engagement_scores": {}
        },
        "is_cold_start": True
    }


def get_comprehensive_recommendations(
    quiz_results: List[dict],
    learning_progress: List[dict],
    emotional_logs: List[dict],
    target_topic: Optional[str] = None
) -> dict:
    """
    Get all recommendations in a single call.

    Args:
        quiz_results: List of quiz result documents
        learning_progress: List of learning progress documents
        emotional_logs: List of emotional log documents
        target_topic: Optional target topic for context

    Returns:
        Combined recommendations dict
    """
    return {
        "topics": recommend_topics(quiz_results, learning_progress),
        "difficulty": recommend_difficulty(quiz_results, target_topic),
        "content_type": recommend_content_type(
            learning_progress, emotional_logs, target_topic, quiz_results
        ),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
