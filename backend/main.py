"""
AI FOR EDUCATION – Adaptive Intelligent Learning System
Main FastAPI Application Entry Point

Run with: uvicorn main:app --reload --port 8000
"""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import HOST, PORT, DEBUG, FRONTEND_URL, AUDIO_OUTPUT_DIR
from database import init_db, close_db

# -------------------------------------------------------
# Logging Configuration
# -------------------------------------------------------
logging.basicConfig(
    level=logging.INFO if DEBUG else logging.WARNING,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# -------------------------------------------------------
# Lifespan – startup / shutdown events
# -------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("=" * 60)
    logger.info("  AI FOR EDUCATION – Starting up...")
    logger.info("=" * 60)

    # Initialize database
    init_db()
    logger.info("[DB] Database initialized.")

    # Train ML models if not present
    from ml.train_model import train_performance_model
    from ml.sentiment_model import train_sentiment_model
    from config import PERFORMANCE_MODEL_PATH, SENTIMENT_MODEL_PATH

    if not PERFORMANCE_MODEL_PATH.exists():
        logger.info("[ML] Training performance model...")
        results = train_performance_model()
        logger.info(f"[ML] Performance model trained: {results}")
    else:
        logger.info("[ML] Performance model already exists.")

    if not SENTIMENT_MODEL_PATH.exists():
        logger.info("[ML] Training sentiment model...")
        results = train_sentiment_model()
        logger.info(f"[ML] Sentiment model trained: {results}")
    else:
        logger.info("[ML] Sentiment model already exists.")

    # Ensure audio directory exists & clean old files (>24h)
    audio_dir = Path(AUDIO_OUTPUT_DIR)
    audio_dir.mkdir(parents=True, exist_ok=True)
    import time
    cutoff = time.time() - 86400  # 24 hours
    cleaned = 0
    for f in audio_dir.glob("*.mp3"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
                cleaned += 1
        except Exception:
            pass
    if cleaned:
        logger.info(f"[Cleanup] Removed {cleaned} old audio file(s).")

    logger.info("[Server] Ready to accept requests.")
    yield
    # Shutdown
    close_db()
    logger.info("[Server] MongoDB connection closed.")

    logger.info("AI FOR EDUCATION – Shutting down.")


# -------------------------------------------------------
# FastAPI Application
# -------------------------------------------------------
app = FastAPI(
    title="AI FOR EDUCATION – Adaptive Intelligent Learning System",
    description="""
A comprehensive AI-powered educational platform featuring:
- **AI Podcast**: Generate educational podcasts on any topic
- **AI Quiz**: Adaptive quizzes with ML performance prediction
- **AI Storytelling**: Narrative-based learning with audio
- **AI Tutor**: Structured learning paths
- **AI Friend**: Emotional support chat with sentiment analysis
- **ML Models**: Student performance prediction & sentiment analysis
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# -------------------------------------------------------
# CORS Middleware
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# Static Files – Audio Output
# -------------------------------------------------------
app.mount("/audio", StaticFiles(directory=str(AUDIO_OUTPUT_DIR)), name="audio")

# -------------------------------------------------------
# Register Routes
# -------------------------------------------------------
from routes.auth import router as auth_router
from routes.podcast import router as podcast_router
from routes.quiz import router as quiz_router
from routes.story import router as story_router
from routes.tutor import router as tutor_router
from routes.friend import router as friend_router
from routes.ml_routes import router as ml_router
from routes.dashboard import router as dashboard_router
from routes.recommendation import router as recommendation_router

# New feature routes
from routes.gamification import router as gamification_router
from routes.flashcards import router as flashcards_router
from routes.analytics import router as analytics_router
from routes.notes import router as notes_router
from routes.voice import router as voice_router
from routes.learning_paths import router as learning_paths_router
from routes.study_buddy import router as study_buddy_router

app.include_router(auth_router)
app.include_router(podcast_router)
app.include_router(quiz_router)
app.include_router(story_router)
app.include_router(tutor_router)
app.include_router(friend_router)
app.include_router(ml_router)
app.include_router(dashboard_router)
app.include_router(recommendation_router)

# New features
app.include_router(gamification_router)
app.include_router(flashcards_router)
app.include_router(analytics_router)
app.include_router(notes_router)
app.include_router(voice_router)
app.include_router(learning_paths_router)
app.include_router(study_buddy_router)


# -------------------------------------------------------
# Root Endpoint
# -------------------------------------------------------
@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "application": "AI FOR EDUCATION – Adaptive Intelligent Learning System",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check – actually pings MongoDB and checks ML artifacts."""
    from database import get_db
    from config import PERFORMANCE_MODEL_PATH, SENTIMENT_MODEL_PATH

    # Check MongoDB
    db_status = "disconnected"
    try:
        db = get_db()
        db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "error"

    # Check ML models
    ml_status = "loaded" if PERFORMANCE_MODEL_PATH.exists() and SENTIMENT_MODEL_PATH.exists() else "not_trained"

    overall = "healthy" if db_status == "connected" and ml_status == "loaded" else "degraded"
    return {
        "status": overall,
        "database": db_status,
        "ml_models": ml_status,
    }


# -------------------------------------------------------
# Run with Uvicorn (if executed directly)
# -------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
