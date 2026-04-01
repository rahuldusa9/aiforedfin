"""
AI FOR EDUCATION – Machine Learning Package
"""

from ml.predictor import predict_performance
from ml.sentiment_model import predict_sentiment, train_sentiment_model
from ml.train_model import train_performance_model
from ml.recommendation_model import (
    recommend_topics,
    recommend_difficulty,
    recommend_content_type,
    get_comprehensive_recommendations
)
from ml.friend_model import (
    classify_intent,
    generate_response_from_model,
    get_all_intents
)
