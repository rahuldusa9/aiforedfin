"""
AI FOR EDUCATION – Performance Predictor
Loads the trained model and makes predictions on new quiz data.
"""

import pickle
import logging
import numpy as np
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ML_DIR = Path(__file__).parent
MODEL_PATH = ML_DIR / "model.pkl"
SCALER_PATH = ML_DIR / "scaler.pkl"
ENCODERS_PATH = ML_DIR / "label_encoders.pkl"

# -------------------------------------------------------
# Cached model objects
# -------------------------------------------------------
_model = None
_scaler = None
_encoders = None


def _load_artifacts():
    """Load model, scaler, and encoders from disk (lazy singleton)."""
    global _model, _scaler, _encoders

    if _model is not None:
        return

    if not MODEL_PATH.exists():
        logger.warning("[ML] Model not found. Training now...")
        from ml.train_model import train_performance_model
        train_performance_model()

    with open(MODEL_PATH, "rb") as f:
        _model = pickle.load(f)
    with open(SCALER_PATH, "rb") as f:
        _scaler = pickle.load(f)
    with open(ENCODERS_PATH, "rb") as f:
        _encoders = pickle.load(f)

    logger.info("[ML] Model artifacts loaded successfully.")


def predict_performance(
    quiz_accuracy: float,
    average_response_time: float,
    difficulty_level: str,
    number_of_attempts: int,
    topic_category: str,
) -> dict:
    """
    Predict student performance level and return recommendations.
    
    Returns:
        {
            "predicted_performance": "low" | "medium" | "high",
            "confidence": float,
            "recommended_difficulty": str,
            "weakness_probability": float,
            "probabilities": {"low": float, "medium": float, "high": float}
        }
    """
    try:
        _load_artifacts()

        # Validate and clamp inputs
        quiz_accuracy = max(0.0, min(1.0, quiz_accuracy))
        average_response_time = max(0.0, average_response_time)
        number_of_attempts = max(1, int(number_of_attempts))
        
        # Normalize difficulty level
        difficulty_level = difficulty_level.lower().strip()
        if difficulty_level not in ["easy", "medium", "hard"]:
            difficulty_level = "medium"
        
        # Normalize topic
        topic_category = topic_category.lower().strip() if topic_category else "general"

        # Encode inputs
        try:
            diff_encoded = _encoders["difficulty_level"].transform([difficulty_level])[0]
        except (ValueError, KeyError):
            diff_encoded = 1  # Default to medium

        try:
            topic_encoded = _encoders["topic_category"].transform([topic_category])[0]
        except (ValueError, KeyError):
            topic_encoded = 0  # Default to first category

        # Feature vector
        features = np.array([[
            quiz_accuracy,
            average_response_time,
            diff_encoded,
            number_of_attempts,
            topic_encoded,
        ]])

        # Scale
        features_scaled = _scaler.transform(features)

        # Predict
        prediction = _model.predict(features_scaled)[0]
        probabilities = _model.predict_proba(features_scaled)[0]

        # Decode prediction
        performance_label = _encoders["performance_level"].inverse_transform([prediction])[0]

        # Build probability dict
        class_labels = _encoders["performance_level"].classes_
        prob_dict = {label: round(float(prob), 4) for label, prob in zip(class_labels, probabilities)}

        # Weakness probability = probability of "low" performance
        weakness_prob = prob_dict.get("low", 0.0)

        # Recommended difficulty
        if performance_label == "high":
            recommended = "hard"
        elif performance_label == "medium":
            recommended = "medium"
        else:
            recommended = "easy"

        confidence = round(float(max(probabilities)), 4)

        return {
            "predicted_performance": performance_label,
            "confidence": confidence,
            "recommended_difficulty": recommended,
            "weakness_probability": round(weakness_prob, 4),
            "probabilities": prob_dict,
        }
    except Exception as e:
        logger.error(f"[ML] Performance prediction error: {e}")
        # Return safe defaults
        return {
            "predicted_performance": "medium",
            "confidence": 0.5,
            "recommended_difficulty": difficulty_level if difficulty_level in ["easy", "medium", "hard"] else "medium",
            "weakness_probability": 0.33,
            "probabilities": {"low": 0.33, "medium": 0.34, "high": 0.33},
        }
