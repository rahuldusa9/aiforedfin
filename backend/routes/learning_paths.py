"""
AI FOR EDUCATION – Learning Paths Routes
Personalized learning paths and adaptive difficulty.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from services.learning_paths_service import get_learning_paths_service

router = APIRouter(prefix="/api/learning-paths", tags=["learning-paths"])


class AssessmentAnswersRequest(BaseModel):
    answers: List[dict]


class UpdateProfileRequest(BaseModel):
    daily_goal_minutes: Optional[int] = None
    preferred_languages: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    interests: Optional[List[str]] = None


class GeneratePathRequest(BaseModel):
    topic: str
    goal: Optional[str] = ""
    lesson_count: Optional[int] = 10


class UpdateProficiencyRequest(BaseModel):
    topic: str
    score: float
    activity_type: str


class CompleteLessonRequest(BaseModel):
    lesson_number: int
    score: Optional[float] = None


# ==================== ASSESSMENT ====================

@router.get("/assessment")
async def get_assessment():
    """Get the onboarding assessment."""
    service = get_learning_paths_service()
    assessment = await service.generate_assessment()
    return assessment


@router.post("/assessment/{user_id}")
async def submit_assessment(user_id: str, request: AssessmentAnswersRequest):
    """Submit assessment answers and create learning profile."""
    service = get_learning_paths_service()
    result = await service.process_assessment(user_id, request.answers)
    return result


# ==================== PROFILE ====================

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """Get user's learning profile."""
    service = get_learning_paths_service()
    profile = await service.get_profile(user_id)
    if not profile:
        return {"profile": None, "assessment_needed": True}
    return {"profile": profile, "assessment_needed": False}


@router.put("/profile/{user_id}")
async def update_profile(user_id: str, request: UpdateProfileRequest):
    """Update learning profile."""
    service = get_learning_paths_service()
    updates = request.dict(exclude_none=True)
    success = await service.update_profile(user_id, updates)
    return {"success": success}


# ==================== ADAPTIVE DIFFICULTY ====================

@router.post("/proficiency/{user_id}")
async def update_proficiency(user_id: str, request: UpdateProficiencyRequest):
    """Update topic proficiency based on activity."""
    service = get_learning_paths_service()
    result = await service.update_topic_proficiency(
        user_id=user_id,
        topic=request.topic,
        score=request.score,
        activity_type=request.activity_type
    )
    return result


@router.get("/difficulty/{user_id}")
async def get_recommended_difficulty(user_id: str, topic: Optional[str] = None):
    """Get recommended difficulty level."""
    service = get_learning_paths_service()
    difficulty = await service.get_recommended_difficulty(user_id, topic)
    return {"recommended_difficulty": difficulty, "topic": topic}


# ==================== LEARNING PATHS ====================

@router.get("/available")
async def get_available_paths(difficulty: Optional[str] = None, subject: Optional[str] = None):
    """Get available learning paths."""
    service = get_learning_paths_service()
    paths = await service.get_available_paths(difficulty, subject)
    return {"paths": paths}


@router.post("/generate/{user_id}")
async def generate_path(user_id: str, request: GeneratePathRequest):
    """Generate a personalized learning path."""
    service = get_learning_paths_service()

    try:
        path = await service.generate_path(
            user_id=user_id,
            topic=request.topic,
            goal=request.goal,
            lesson_count=request.lesson_count
        )
        return path
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enroll/{path_id}/{user_id}")
async def enroll_in_path(path_id: str, user_id: str):
    """Enroll in a learning path."""
    service = get_learning_paths_service()
    enrollment = await service.enroll_in_path(user_id, path_id)
    return enrollment


@router.get("/my-paths/{user_id}")
async def get_user_paths(user_id: str):
    """Get paths user is enrolled in."""
    service = get_learning_paths_service()
    paths = await service.get_user_paths(user_id)
    return {"paths": paths}


@router.post("/complete-lesson/{path_id}/{user_id}")
async def complete_lesson(path_id: str, user_id: str, request: CompleteLessonRequest):
    """Mark a lesson as complete."""
    service = get_learning_paths_service()
    result = await service.complete_lesson(
        user_id=user_id,
        path_id=path_id,
        lesson_number=request.lesson_number,
        score=request.score
    )
    return result
