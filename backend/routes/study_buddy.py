"""
AI FOR EDUCATION – Study Buddy Routes
Enhanced AI companion with proactive features.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from services.study_buddy_service import get_study_buddy_service

router = APIRouter(prefix="/api/buddy", tags=["study-buddy"])


class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None


class StudyPlanRequest(BaseModel):
    goals: List[str]
    available_time_minutes: Optional[int] = 60
    days: Optional[int] = 7


class ExplainRequest(BaseModel):
    topic: str
    level: Optional[str] = "eli5"


class SetPersonalityRequest(BaseModel):
    personality: str


# ==================== CHAT ====================

@router.post("/chat/{user_id}")
async def chat_with_buddy(user_id: str, request: ChatRequest):
    """Have a conversation with the study buddy."""
    service = get_study_buddy_service()
    response = await service.chat(
        user_id=user_id,
        message=request.message,
        context=request.context
    )
    return response


# ==================== PROACTIVE CHECK-INS ====================

@router.get("/check-in/{user_id}")
async def get_check_in(user_id: str):
    """Get a proactive check-in message."""
    service = get_study_buddy_service()
    check_in = await service.get_check_in(user_id)
    return check_in


# ==================== STUDY PLANNING ====================

@router.post("/study-plan/{user_id}")
async def create_study_plan(user_id: str, request: StudyPlanRequest):
    """Create a personalized study plan."""
    service = get_study_buddy_service()

    try:
        plan = await service.create_study_plan(
            user_id=user_id,
            goals=request.goals,
            available_time_minutes=request.available_time_minutes,
            days=request.days
        )
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/study-plan/{user_id}")
async def get_study_plan(user_id: str):
    """Get user's current study plan."""
    service = get_study_buddy_service()
    plan = await service.get_study_plan(user_id)
    if not plan:
        return {"has_plan": False}
    return {"has_plan": True, "plan": plan}


@router.get("/today/{user_id}")
async def get_todays_tasks(user_id: str):
    """Get today's tasks from the study plan."""
    service = get_study_buddy_service()
    tasks = await service.get_todays_tasks(user_id)
    return tasks


# ==================== MOTIVATION ====================

@router.get("/motivation/{user_id}")
async def get_motivation(user_id: str, context: Optional[str] = None):
    """Get a motivational message."""
    service = get_study_buddy_service()
    motivation = await service.get_motivation(user_id, context or "")
    return motivation


@router.post("/explain")
async def explain_simply(request: ExplainRequest):
    """Get a simple explanation of a topic."""
    service = get_study_buddy_service()
    explanation = await service.explain_simply(request.topic, request.level)
    return explanation


# ==================== PERSONALITY ====================

@router.post("/personality/{user_id}")
async def set_personality(user_id: str, request: SetPersonalityRequest):
    """Set buddy personality."""
    service = get_study_buddy_service()

    try:
        result = await service.set_personality(user_id, request.personality)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/personalities")
async def get_personalities():
    """Get available buddy personalities."""
    service = get_study_buddy_service()
    personalities = await service.get_personalities()
    return {"personalities": personalities}
