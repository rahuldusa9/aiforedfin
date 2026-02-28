"""
AI FOR EDUCATION – Friend Service
AI chat companion with sentiment detection and emotional support.
"""

import logging

from services.gemini_service import generate_chat_response
from ml.sentiment_model import predict_sentiment
from models.emotional import create_emotional_log_doc

logger = logging.getLogger(__name__)


def chat_with_friend(
    db,
    user_id: str,
    message: str,
) -> dict:
    """
    Process a chat message:
    1. Detect sentiment via ML model
    2. Generate appropriate response (supportive if negative)
    3. Log emotional state
    
    Args:
        db: MongoDB database instance
        user_id: User ID (string)
        message: User's chat message
    
    Returns:
        {
            "response": str,
            "sentiment": str,
            "is_negative": bool,
            "confidence": float
        }
    """
    logger.info(f"[Friend] Processing message from user {user_id}")

    # Step 1: Detect sentiment
    sentiment_result = predict_sentiment(message)
    sentiment = sentiment_result["sentiment"]
    is_negative = sentiment_result["is_negative"]
    confidence = sentiment_result["confidence"]

    logger.info(f"[Friend] Detected sentiment: {sentiment} (confidence={confidence})")

    # Step 2: Generate response
    response = generate_chat_response(message, sentiment, is_negative)

    # Step 3: Log to database
    doc = create_emotional_log_doc(
        user_id=user_id,
        message=message,
        detected_sentiment=sentiment,
        confidence=confidence,
        ai_response=response,
        supportive_mode=is_negative,
    )
    db.emotional_logs.insert_one(doc)

    return {
        "response": response,
        "sentiment": sentiment,
        "is_negative": is_negative,
        "confidence": confidence,
    }
