"""
AI FOR EDUCATION – Friend Service
AI chat companion with sentiment detection and emotional support.
Uses custom ML model - NO API dependency!
"""

import logging
import os

from ml.sentiment_model import predict_sentiment
from ml.friend_model import generate_response_from_model, classify_intent
from models.emotional import create_emotional_log_doc

# Optional: Use Gemini API as enhancement (set USE_API=true in .env)
USE_API = os.getenv("USE_GEMINI_FOR_FRIEND", "false").lower() == "true"

if USE_API:
    from services.gemini_service import generate_chat_response

logger = logging.getLogger(__name__)


def chat_with_friend(
    db,
    user_id: str,
    message: str,
    use_api: bool = None,
) -> dict:
    """
    Process a chat message using CUSTOM ML MODEL (no API needed).

    Args:
        db: MongoDB database instance
        user_id: User ID (string)
        message: User's chat message
        use_api: Override to force API usage (optional)

    Returns:
        {
            "response": str,
            "sentiment": str,
            "is_negative": bool,
            "confidence": float,
            "intent": str,
            "source": str  # "model" or "api"
        }
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")

    if not user_id or not user_id.strip():
        raise ValueError("User ID is required")

    logger.info(f"[Friend] Processing message from user {user_id}")

    # Step 1: Detect sentiment using ML model
    try:
        sentiment_result = predict_sentiment(message)
        sentiment = sentiment_result.get("sentiment", "neutral")
        is_negative = sentiment_result.get("is_negative", False)
        sentiment_confidence = sentiment_result.get("confidence", 0.0)
    except Exception as e:
        logger.error(f"[Friend] Sentiment detection failed: {e}")
        sentiment = "neutral"
        is_negative = False
        sentiment_confidence = 0.0

    logger.info(f"[Friend] Detected sentiment: {sentiment} (confidence={sentiment_confidence:.2f})")

    # Step 2: Classify intent using ML model
    try:
        intent, intent_confidence = classify_intent(message)
        logger.info(f"[Friend] Detected intent: {intent} (confidence={intent_confidence:.2f})")
    except Exception as e:
        logger.error(f"[Friend] Intent classification failed: {e}")
        intent = "casual"
        intent_confidence = 0.5

    # Step 3: Generate response
    should_use_api = use_api if use_api is not None else USE_API
    source = "model"

    if should_use_api:
        # Try API first, fallback to model
        try:
            logger.info("[Friend] Using Gemini API for response...")
            response = generate_chat_response(message, sentiment, is_negative)
            source = "api"
            if not response or not response.strip():
                raise ValueError("Empty response from API")
        except Exception as e:
            logger.warning(f"[Friend] API failed, using ML model: {e}")
            model_result = generate_response_from_model(message, sentiment)
            response = model_result["response"]
            source = "model"
    else:
        # Use ML model directly (NO API)
        logger.info("[Friend] Using ML model for response (no API)...")
        model_result = generate_response_from_model(message, sentiment)
        response = model_result["response"]
        source = "model"

    logger.info(f"[Friend] Generated response from {source} (length: {len(response)} chars)")

    # Step 4: Log to database
    try:
        doc = create_emotional_log_doc(
            user_id=user_id,
            message=message,
            detected_sentiment=sentiment,
            confidence=sentiment_confidence,
            ai_response=response,
            supportive_mode=is_negative,
        )
        # Add extra fields
        doc["intent"] = intent
        doc["intent_confidence"] = intent_confidence
        doc["response_source"] = source

        db.emotional_logs.insert_one(doc)
    except Exception as e:
        logger.error(f"[Friend] Failed to log to database: {e}")

    return {
        "response": response,
        "sentiment": sentiment,
        "is_negative": is_negative,
        "confidence": sentiment_confidence,
        "intent": intent,
        "source": source,
    }
