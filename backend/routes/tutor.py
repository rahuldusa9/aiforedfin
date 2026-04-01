"""
AI FOR EDUCATION – Tutor API Routes
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import get_db
from services.tutor_service import create_learning_path
from models.learning import create_learning_progress_doc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tutor", tags=["AI Tutor"])


class TutorRequest(BaseModel):
    topic: str


class SaveProgressRequest(BaseModel):
    user_id: str
    module: str = "tutor"
    topic: str
    status: str = "completed"
    progress_percent: float = 100.0
    notes: str = ""
    time_spent_seconds: float = 0.0


@router.post("/learning-path")
def generate_learning_path_endpoint(req: TutorRequest):
    """Generate a structured learning path for a topic."""
    try:
        result = create_learning_path(req.topic)
        return result
    except Exception as e:
        logger.error(f"[Tutor] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Learning path generation failed: {str(e)}")


@router.post("/save-progress")
def save_progress(req: SaveProgressRequest, db=Depends(get_db)):
    """Save learning progress when a user completes a tutor step."""
    try:
        doc = create_learning_progress_doc(
            user_id=req.user_id,
            module=req.module,
            topic=req.topic,
            status=req.status,
            progress_percent=req.progress_percent,
            notes=req.notes,
            time_spent_seconds=req.time_spent_seconds,
        )
        result = db.learning_progress.insert_one(doc)
        return {"id": str(result.inserted_id), "status": "saved"}
    except Exception as e:
        logger.error(f"[Tutor] Save progress error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save progress: {str(e)}")
