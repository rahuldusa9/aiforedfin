"""
AI FOR EDUCATION – Sentiment Analysis Model
Naive Bayes classifier for emotional state detection.
Classifies text into: positive, neutral, stressed, anxious.
"""

import pickle
import logging
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

ML_DIR = Path(__file__).parent
SENTIMENT_MODEL_PATH = ML_DIR / "sentiment_model.pkl"

# -------------------------------------------------------
# Training data – small emotional dataset
# -------------------------------------------------------
TRAINING_DATA = [
    # Positive
    ("I feel great about my progress today!", "positive"),
    ("I understood everything in the lesson", "positive"),
    ("This is really fun to learn", "positive"),
    ("I aced the quiz!", "positive"),
    ("I'm so happy with my results", "positive"),
    ("Learning is exciting today", "positive"),
    ("I feel confident about this topic", "positive"),
    ("I'm doing really well", "positive"),
    ("This is interesting and enjoyable", "positive"),
    ("I love studying this subject", "positive"),
    ("Great session today!", "positive"),
    ("I feel motivated and ready", "positive"),
    ("Everything makes sense now", "positive"),
    ("I'm proud of my improvement", "positive"),
    ("I feel amazing after this lesson", "positive"),
    ("I got a perfect score!", "positive"),
    ("This topic is fascinating", "positive"),
    ("I feel encouraged by my progress", "positive"),
    ("Today was a productive study day", "positive"),
    ("I'm glad I took the time to learn this", "positive"),

    # Neutral
    ("I'm working on the assignment", "neutral"),
    ("Just studying for the test", "neutral"),
    ("I need to finish this chapter", "neutral"),
    ("Can you explain this topic?", "neutral"),
    ("What's the next lesson about?", "neutral"),
    ("I have a question about this", "neutral"),
    ("Let me try another quiz", "neutral"),
    ("I'm reviewing my notes", "neutral"),
    ("I'll continue with the next section", "neutral"),
    ("Tell me more about this concept", "neutral"),
    ("I'm reading through the material", "neutral"),
    ("Can we move to the next topic?", "neutral"),
    ("I want to practice more problems", "neutral"),
    ("Let me think about it", "neutral"),
    ("I need more examples", "neutral"),
    ("Show me the next step", "neutral"),
    ("I'm going to study now", "neutral"),
    ("What topics should I review?", "neutral"),
    ("How do I solve this problem?", "neutral"),
    ("I'll try again later", "neutral"),

    # Stressed
    ("I'm so stressed about the exam", "stressed"),
    ("I can't handle all this work", "stressed"),
    ("There's too much to study", "stressed"),
    ("I feel overwhelmed with assignments", "stressed"),
    ("I'm falling behind in my studies", "stressed"),
    ("This is too much pressure", "stressed"),
    ("I have so many deadlines", "stressed"),
    ("I feel burned out", "stressed"),
    ("I can't keep up with everything", "stressed"),
    ("I'm really struggling with this", "stressed"),
    ("I'm under so much pressure", "stressed"),
    ("I feel completely exhausted from studying", "stressed"),
    ("There's no way I can finish all this", "stressed"),
    ("I'm so frustrated with this material", "stressed"),
    ("I feel like giving up", "stressed"),
    ("Everything is piling up", "stressed"),
    ("I'm not coping well at all", "stressed"),
    ("This workload is crushing me", "stressed"),
    ("I feel tense and overworked", "stressed"),
    ("I can't concentrate anymore", "stressed"),

    # Anxious
    ("I'm really worried about my grades", "anxious"),
    ("What if I fail the test?", "anxious"),
    ("I'm nervous about the upcoming exam", "anxious"),
    ("I feel anxious about my performance", "anxious"),
    ("I'm scared I won't understand", "anxious"),
    ("I have a bad feeling about the results", "anxious"),
    ("I'm afraid I'll forget everything", "anxious"),
    ("My heart races when I think about exams", "anxious"),
    ("I can't stop worrying about school", "anxious"),
    ("I feel uneasy about this subject", "anxious"),
    ("I'm panicking about the deadline", "anxious"),
    ("What if I'm not good enough?", "anxious"),
    ("I'm terrified of failing", "anxious"),
    ("I keep worrying about my future", "anxious"),
    ("I feel so uncertain about everything", "anxious"),
    ("I'm dreading the test tomorrow", "anxious"),
    ("My anxiety is really high right now", "anxious"),
    ("I feel restless and unsettled", "anxious"),
    ("I'm overthinking everything", "anxious"),
    ("I can't shake this nervous feeling", "anxious"),
]


def train_sentiment_model():
    """
    Train the sentiment classifier pipeline (TF-IDF + MultinomialNB).
    Saves the complete pipeline to disk.
    """
    logger.info("[ML] Training sentiment analysis model...")

    texts = [t[0] for t in TRAINING_DATA]
    labels = [t[1] for t in TRAINING_DATA]

    # Build pipeline
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words="english",
        )),
        ("classifier", MultinomialNB(alpha=0.1)),
    ])

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels,
    )

    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"[ML] Sentiment Model Accuracy: {accuracy:.4f}")
    logger.info(f"[ML] Report:\n{classification_report(y_test, y_pred)}")

    # Save
    with open(SENTIMENT_MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)

    logger.info(f"[ML] Sentiment model saved to {SENTIMENT_MODEL_PATH}")
    return {"accuracy": accuracy}


# -------------------------------------------------------
# Prediction
# -------------------------------------------------------
_sentiment_model = None


def _load_sentiment_model():
    global _sentiment_model
    if _sentiment_model is not None:
        return

    if not SENTIMENT_MODEL_PATH.exists():
        logger.warning("[ML] Sentiment model not found. Training now...")
        train_sentiment_model()

    with open(SENTIMENT_MODEL_PATH, "rb") as f:
        _sentiment_model = pickle.load(f)

    logger.info("[ML] Sentiment model loaded.")


def predict_sentiment(text: str) -> dict:
    """
    Predict sentiment of input text.
    
    Returns:
        {
            "sentiment": str,
            "confidence": float,
            "is_negative": bool,
            "probabilities": dict
        }
    """
    _load_sentiment_model()

    prediction = _sentiment_model.predict([text])[0]
    probas = _sentiment_model.predict_proba([text])[0]
    classes = _sentiment_model.classes_

    prob_dict = {cls: round(float(p), 4) for cls, p in zip(classes, probas)}
    confidence = round(float(max(probas)), 4)
    is_negative = prediction in ("stressed", "anxious")

    return {
        "sentiment": prediction,
        "confidence": confidence,
        "is_negative": is_negative,
        "probabilities": prob_dict,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_sentiment_model()

    # Test predictions
    test_messages = [
        "I'm so happy today!",
        "I'm worried about my exam",
        "Can you explain photosynthesis?",
        "I feel so overwhelmed with work",
    ]
    for msg in test_messages:
        result = predict_sentiment(msg)
        print(f"'{msg}' → {result['sentiment']} ({result['confidence']:.2f})")
