"""
AI FOR EDUCATION – Application Configuration
Centralized configuration management using environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -------------------------------------------------------
# Base Paths
# -------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
AUDIO_OUTPUT_DIR = BASE_DIR / "audio_output"

# Ensure directories exist
AUDIO_OUTPUT_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------
# MongoDB
# -------------------------------------------------------
MONGODB_URI = os.getenv("MONGODB_URI", "")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is required. Set it in .env file.")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "afe")

# -------------------------------------------------------
# Gemini API
# -------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# -------------------------------------------------------
# Server
# -------------------------------------------------------
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# -------------------------------------------------------
# CORS
# -------------------------------------------------------
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# -------------------------------------------------------
# ML Model Paths
# -------------------------------------------------------
PERFORMANCE_MODEL_PATH = BASE_DIR / "ml" / "model.pkl"
SENTIMENT_MODEL_PATH = BASE_DIR / "ml" / "sentiment_model.pkl"
SCALER_PATH = BASE_DIR / "ml" / "scaler.pkl"
LABEL_ENCODERS_PATH = BASE_DIR / "ml" / "label_encoders.pkl"
