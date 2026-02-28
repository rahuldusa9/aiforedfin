"""
AI FOR EDUCATION – Quiz API Routes
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from database import get_db
from services.quiz_service import create_quiz, evaluate_quiz
from models.quiz import quiz_result_to_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quiz", tags=["AI Quiz"])


# -------------------------------------------------------
# Schemas
# -------------------------------------------------------
class QuizGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    num_questions: int = Field(5, ge=1, le=20)
    difficulty: str = Field("medium", pattern="^(easy|medium|hard)$")


class QuizSubmitRequest(BaseModel):
    user_id: str = "000000000000000000000001"
    topic: str
    difficulty: str
    questions: list[dict]
    answers: dict  # {"0": "A", "1": "B", ...}
    time_taken_seconds: float


# -------------------------------------------------------
# Endpoints
# -------------------------------------------------------
@router.post("/generate")
def generate_quiz_endpoint(req: QuizGenerateRequest):
    """Generate a new quiz."""
    try:
        result = create_quiz(req.topic, req.num_questions, req.difficulty)
        return result
    except Exception as e:
        logger.error(f"[Quiz] Generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")


@router.post("/submit")
def submit_quiz(req: QuizSubmitRequest, db=Depends(get_db)):
    """Submit quiz answers and get evaluation with ML prediction."""
    try:
        result = evaluate_quiz(
            db=db,
            user_id=req.user_id,
            topic=req.topic,
            difficulty=req.difficulty,
            questions=req.questions,
            answers=req.answers,
            time_taken_seconds=req.time_taken_seconds,
        )
        return result
    except Exception as e:
        logger.error(f"[Quiz] Evaluation error: {e}")
        raise HTTPException(status_code=500, detail=f"Quiz evaluation failed: {str(e)}")


@router.get("/history/{user_id}")
def get_quiz_history(user_id: str, db=Depends(get_db)):
    """Get quiz history for a user."""
    results = list(
        db.quiz_results.find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(20)
    )
    return [quiz_result_to_response(r) for r in results]
