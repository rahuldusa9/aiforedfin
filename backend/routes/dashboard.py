"""
AI FOR EDUCATION – Dashboard API Routes
Provides aggregated stats for the dashboard.
"""

import logging
from fastapi import APIRouter, Depends

from database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats/{user_id}")
def get_dashboard_stats(user_id: str, db=Depends(get_db)):
    """Get aggregated dashboard statistics for a user."""

    # ---- Quiz stats ----
    quiz_count = db.quiz_results.count_documents({"user_id": user_id})

    avg_pipeline = db.quiz_results.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "avg_score": {"$avg": "$score"}}},
    ])
    avg_score = 0
    for doc in avg_pipeline:
        avg_score = doc.get("avg_score", 0)

    # Recent quiz results (for graph)
    recent_quizzes = list(
        db.quiz_results.find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(10)
    )
    quiz_history = [
        {
            "topic": q["topic"],
            "score": q["score"],
            "difficulty": q["difficulty"],
            "predicted_performance": q.get("predicted_performance"),
            "created_at": str(q.get("created_at", "")),
        }
        for q in reversed(recent_quizzes)
    ]

    # ---- Emotional stats ----
    emotional_count = db.emotional_logs.count_documents({"user_id": user_id})

    # Sentiment distribution
    sentiment_pipeline = db.emotional_logs.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$detected_sentiment", "count": {"$sum": 1}}},
    ])
    sentiment_distribution = {doc["_id"]: doc["count"] for doc in sentiment_pipeline}

    # ---- Learning progress ----
    modules_pipeline = db.learning_progress.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$module"}},
        {"$count": "total"},
    ])
    modules_used = 0
    for doc in modules_pipeline:
        modules_used = doc.get("total", 0)

    time_pipeline = db.learning_progress.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "total": {"$sum": "$time_spent_seconds"}}},
    ])
    total_time = 0
    for doc in time_pipeline:
        total_time = doc.get("total", 0)

    return {
        "quiz_stats": {
            "total_quizzes": quiz_count,
            "average_score": round(float(avg_score), 1),
            "quiz_history": quiz_history,
        },
        "emotional_stats": {
            "total_interactions": emotional_count,
            "sentiment_distribution": sentiment_distribution,
        },
        "learning_stats": {
            "modules_used": modules_used,
            "total_time_minutes": round(float(total_time) / 60, 1),
        },
    }
