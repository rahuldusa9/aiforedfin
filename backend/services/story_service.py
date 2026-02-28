"""
AI FOR EDUCATION – Story Service
Generates narrative educational content with audio.
"""

import logging
from services.gemini_service import generate_story
from services.tts_service import generate_story_audio

logger = logging.getLogger(__name__)


def create_story(topic: str) -> dict:
    """
    Generate an educational story with audio narration.
    
    Args:
        topic: The topic to create a story about
    
    Returns:
        {
            "topic": str,
            "story_text": str,
            "audio_url": str
        }
    """
    logger.info(f"[Story] Creating story for topic: {topic}")

    # Generate story text
    story_text = generate_story(topic)
    logger.info(f"[Story] Text generated: {len(story_text)} chars")

    # Generate audio
    audio_path = generate_story_audio(story_text)
    audio_filename = audio_path.split("/")[-1].split("\\")[-1]
    logger.info(f"[Story] Audio generated: {audio_path}")

    return {
        "topic": topic,
        "story_text": story_text,
        "audio_url": f"/audio/{audio_filename}",
    }
