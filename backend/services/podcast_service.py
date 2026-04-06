"""
AI FOR EDUCATION – Podcast Service
Orchestrates podcast generation: script → audio → delivery.
"""

import logging
from services.gemini_service import generate_podcast_script
from services.tts_service import generate_podcast_audio

logger = logging.getLogger(__name__)


def create_podcast(topic: str, language: str = "en", length: str = "medium") -> dict:
    """
    Full podcast creation pipeline.
    
    1. Generate script via Gemini
    2. Convert to multi-speaker audio
    3. Return script + audio path
    
    Args:
        topic: The podcast topic
        language: Language code
        length: "short", "medium", or "long"
    
    Returns:
        {
            "topic": str,
            "script": list[dict],
            "audio_path": str,
            "audio_url": str
        }
    """
    logger.info(f"[Podcast] Creating podcast for topic: {topic} in {language} (length: {length})")

    # Step 1: Generate script
    script = generate_podcast_script(topic, language, length)
    logger.info(f"[Podcast] Script generated: {len(script)} segments")

    # Step 2: Generate audio
    audio_path = generate_podcast_audio(script, language)
    logger.info(f"[Podcast] Audio generated: {audio_path}")

    # Extract filename for URL
    audio_filename = audio_path.split("/")[-1].split("\\")[-1]

    return {
        "topic": topic,
        "script": script,
        "audio_path": audio_path,
        "audio_url": f"/audio/{audio_filename}",
    }
