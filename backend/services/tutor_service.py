"""
AI FOR EDUCATION – Tutor Service
Generates structured learning paths.
"""

import logging
from services.gemini_service import generate_learning_path

logger = logging.getLogger(__name__)


def create_learning_path(topic: str) -> dict:
    """
    Generate a structured learning path with concepts, examples, and mini tests.
    
    Args:
        topic: The topic to learn
    
    Returns:
        Structured learning path dict
    """
    logger.info(f"[Tutor] Creating learning path for: {topic}")
    path = generate_learning_path(topic)
    logger.info(f"[Tutor] Learning path generated: {path.get('total_steps', 0)} steps")
    return path
