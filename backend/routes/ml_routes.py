"""
AI FOR EDUCATION – ML Prediction Routes
Direct ML model endpoints for performance prediction.
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ml.predictor import predict_performance
from ml.sentiment_model import predict_sentiment

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


# -------------------------------------------------------
# Schemas
# -------------------------------------------------------
class PerformancePredictionRequest(BaseModel):
    quiz_accuracy: float          # 0.0 to 1.0
    average_response_time: float  # seconds
    difficulty_level: str         # easy, medium, hard
    number_of_attempts: int
    topic_category: str


class SentimentRequest(BaseModel):
    text: str


# -------------------------------------------------------
# Endpoints
# -------------------------------------------------------
@router.post("/predict-performance")
def predict_performance_endpoint(req: PerformancePredictionRequest):
    """
    Predict student performance level based on quiz metrics.
    Uses the trained RandomForest/LogisticRegression model.
    """
    try:
        result = predict_performance(
            quiz_accuracy=req.quiz_accuracy,
            average_response_time=req.average_response_time,
            difficulty_level=req.difficulty_level,
            number_of_attempts=req.number_of_attempts,
            topic_category=req.topic_category,
        )
        return result
    except Exception as e:
        logger.error(f"[ML] Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/predict-sentiment")
def predict_sentiment_endpoint(req: SentimentRequest):
    """
    Predict sentiment of input text.
    Uses Naive Bayes classifier.
    """
    try:
        result = predict_sentiment(req.text)
        return result
    except Exception as e:
        logger.error(f"[ML] Sentiment prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment prediction failed: {str(e)}")
