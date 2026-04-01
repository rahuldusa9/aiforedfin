"""
AI FOR EDUCATION – Friend Chat API Routes
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import get_db
from services.friend_service import chat_with_friend
from models.emotional import emotional_log_to_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/friend", tags=["AI Friend"])


class ChatRequest(BaseModel):
    user_id: str = "000000000000000000000001"
    message: str


class ChatResponse(BaseModel):
    response: str
    sentiment: str
    is_negative: bool
    confidence: float


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db=Depends(get_db)):
    """Send a message to AI Friend and get a sentiment-aware response."""
    try:
        result = chat_with_friend(db, req.user_id, req.message)
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"[Friend] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/emotional-history/{user_id}")
def get_emotional_history(user_id: str, db=Depends(get_db)):
    """Get emotional log history for a user."""
    logs = list(
        db.emotional_logs.find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(50)
    )
    return [emotional_log_to_response(log) for log in logs]
