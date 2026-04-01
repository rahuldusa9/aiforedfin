"""
AI FOR EDUCATION – Analytics Routes
Learning analytics and insights.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.analytics_service import get_analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


class LogActivityRequest(BaseModel):
    activity_type: str
    activity_id: Optional[str] = None
    topic: Optional[str] = ""
    language: Optional[str] = "en"
    duration_ms: Optional[int] = 0
    score: Optional[float] = None
    metadata: Optional[dict] = None


@router.post("/log/{user_id}")
async def log_activity(user_id: str, request: LogActivityRequest):
    """Log a learning activity."""
    service = get_analytics_service()
    result = await service.log_activity(
        user_id=user_id,
        activity_type=request.activity_type,
        activity_id=request.activity_id,
        topic=request.topic,
        language=request.language,
        duration_ms=request.duration_ms,
        score=request.score,
        metadata=request.metadata
    )
    return {"logged": True}


@router.get("/summary/{user_id}")
async def get_learning_summary(user_id: str, days: int = 30):
    """Get comprehensive learning summary."""
    service = get_analytics_service()
    summary = await service.get_learning_summary(user_id, days)
    return summary


@router.get("/strengths/{user_id}")
async def get_strength_weakness_map(user_id: str):
    """Get strengths and weaknesses by topic."""
    service = get_analytics_service()
    analysis = await service.get_strength_weakness_map(user_id)
    return analysis


@router.get("/velocity/{user_id}")
async def get_learning_velocity(user_id: str):
    """Get learning velocity and predictions."""
    service = get_analytics_service()
    velocity = await service.get_learning_velocity(user_id)
    return velocity


@router.get("/time/{user_id}")
async def get_time_analytics(user_id: str, days: int = 7):
    """Get time-based analytics."""
    service = get_analytics_service()
    time_data = await service.get_time_analytics(user_id, days)
    return time_data


@router.get("/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    """Get personalized learning recommendations."""
    service = get_analytics_service()
    recommendations = await service.get_recommendations(user_id)
    return {"recommendations": recommendations}
