"""
AI FOR EDUCATION - Recommendation API Routes
Endpoints for personalized learning recommendations.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

from database import get_db
from services.recommendation_service import (
    get_user_recommendations,
    get_topic_recommendations_only,
    get_difficulty_recommendation_only,
    get_content_recommendation_only
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


# -------------------------------------------------------
# Response Schemas
# -------------------------------------------------------
class TopicRecommendation(BaseModel):
    topic: str
    priority: float
    reason: str
    weakness_probability: Optional[float] = None


class TopicRecommendationsResponse(BaseModel):
    recommendations: List[TopicRecommendation]
    confidence: float
    data_points_used: int
    is_cold_start: bool


class DifficultyReasoning(BaseModel):
    average_score: Optional[float] = None
    trend: str
    trend_slope: Optional[float] = None
    current_level: Optional[str] = None
    action: str


class DifficultyRecommendationResponse(BaseModel):
    recommended_difficulty: str
    confidence: float
    reasoning: DifficultyReasoning
    is_cold_start: bool


class ContentAlternative(BaseModel):
    type: str
    score: float


class ContentFactors(BaseModel):
    emotional_state: str
    emotional_confidence: Optional[float] = None
    topic_familiarity: Optional[float] = None
    engagement_scores: Optional[dict] = None


class ContentRecommendationResponse(BaseModel):
    recommended_content: str
    confidence: float
    alternatives: List[ContentAlternative]
    factors: ContentFactors
    is_cold_start: bool


# -------------------------------------------------------
# Endpoints
# -------------------------------------------------------
@router.get("/{user_id}")
def get_recommendations(
    user_id: str,
    topic: Optional[str] = Query(None, description="Target topic for context"),
    days: int = Query(30, ge=1, le=365, description="Days of history to analyze"),
    db=Depends(get_db)
):
    """
    Get comprehensive recommendations for a user.

    Returns topic, difficulty, and content type recommendations
    based on quiz performance, learning progress, and emotional state.
    """
    try:
        result = get_user_recommendations(db, user_id, topic, days)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")


@router.get("/{user_id}/topics", response_model=TopicRecommendationsResponse)
def get_topic_recommendations(
    user_id: str,
    limit: int = Query(5, ge=1, le=10, description="Number of topic recommendations"),
    db=Depends(get_db)
):
    """
    Get topic recommendations for a user.

    Returns prioritized list of topics to study based on
    weaknesses, knowledge gaps, and recency.
    """
    try:
        return get_topic_recommendations_only(db, user_id, limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Topic recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate topic recommendations")


@router.get("/{user_id}/difficulty", response_model=DifficultyRecommendationResponse)
def get_difficulty_recommendation(
    user_id: str,
    topic: Optional[str] = Query(None, description="Filter by specific topic"),
    db=Depends(get_db)
):
    """
    Get difficulty recommendation for a user.

    Analyzes performance trends to suggest optimal difficulty level.
    """
    try:
        return get_difficulty_recommendation_only(db, user_id, topic)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Difficulty recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate difficulty recommendation")


@router.get("/{user_id}/content", response_model=ContentRecommendationResponse)
def get_content_recommendation(
    user_id: str,
    topic: Optional[str] = Query(None, description="Target topic for context"),
    db=Depends(get_db)
):
    """
    Get content type recommendation for a user.

    Suggests Quiz, Story, Podcast, or Tutor based on
    engagement patterns and emotional state.
    """
    try:
        return get_content_recommendation_only(db, user_id, topic)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Content recommendation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate content recommendation")
