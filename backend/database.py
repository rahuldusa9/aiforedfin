"""
AI FOR EDUCATION – Database Connection
MongoDB Atlas via PyMongo.
"""

import logging
import certifi
from pymongo import MongoClient, ASCENDING
from config import MONGODB_URI, MONGODB_DB_NAME

logger = logging.getLogger(__name__)

# -------------------------------------------------------
# MongoDB Client (singleton)
# -------------------------------------------------------
_client: MongoClient | None = None
_db = None


def get_db():
    """
    Return the MongoDB database instance.
    Used as a FastAPI dependency.
    """
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
        _db = _client[MONGODB_DB_NAME]
        logger.info(f"[DB] Connected to MongoDB: {MONGODB_DB_NAME}")
    return _db


def init_db():
    """
    Initialize MongoDB – create indexes for all collections.
    Called once on application startup.
    """
    db = get_db()

    # Users collection indexes
    db.users.create_index([("username", ASCENDING)], unique=True)
    db.users.create_index([("email", ASCENDING)], unique=True)

    # Quiz results indexes
    db.quiz_results.create_index([("user_id", ASCENDING)])
    db.quiz_results.create_index([("created_at", ASCENDING)])

    # Learning progress indexes
    db.learning_progress.create_index([("user_id", ASCENDING)])

    # Emotional logs indexes
    db.emotional_logs.create_index([("user_id", ASCENDING)])
    db.emotional_logs.create_index([("created_at", ASCENDING)])

    logger.info("[DB] MongoDB indexes ensured.")


def close_db():
    """Close the MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("[DB] MongoDB connection closed.")

class _DBProxy:
    """Proxy object to allow `from database import db` in services without eager initialization."""
    def __getattr__(self, name):
        return get_db()[name]
    
    def __getitem__(self, key):
        return get_db()[key]

db = _DBProxy()
