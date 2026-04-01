"""
AI FOR EDUCATION – Gamification Routes
XP, badges, streaks, levels, and leaderboards.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from services.gamification_service import get_gamification_service

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


class TrackActivityRequest(BaseModel):
    activity_type: str
    metadata: Optional[dict] = None


class AwardXPRequest(BaseModel):
    activity: str
    bonus_multiplier: Optional[float] = 1.0


@router.get("/stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get gamification stats for a user."""
    service = get_gamification_service()
    stats = await service.get_user_stats(user_id)
    return stats


@router.post("/track/{user_id}")
async def track_activity(user_id: str, request: TrackActivityRequest):
    """Track an activity and award XP/badges."""
    service = get_gamification_service()
    result = await service.track_activity(
        user_id=user_id,
        activity_type=request.activity_type,
        metadata=request.metadata
    )
    return result


@router.post("/xp/{user_id}")
async def award_xp(user_id: str, request: AwardXPRequest):
    """Award XP for an activity."""
    service = get_gamification_service()
    result = await service.award_xp(
        user_id=user_id,
        activity=request.activity,
        bonus_multiplier=request.bonus_multiplier
    )
    return result


@router.post("/streak/{user_id}")
async def update_streak(user_id: str):
    """Update user's learning streak."""
    service = get_gamification_service()
    result = await service.update_streak(user_id)
    return result


@router.post("/streak-freeze/{user_id}")
async def use_streak_freeze(user_id: str):
    """Use a streak freeze token."""
    service = get_gamification_service()
    result = await service.use_streak_freeze(user_id)
    return result


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10, timeframe: str = "all"):
    """Get the XP leaderboard."""
    service = get_gamification_service()
    leaderboard = await service.get_leaderboard(limit=limit, timeframe=timeframe)
    return {"leaderboard": leaderboard, "timeframe": timeframe}


@router.get("/badges")
async def get_available_badges():
    """Get all available badges."""
    service = get_gamification_service()
    badges = await service.get_available_badges()
    return {"badges": badges}
