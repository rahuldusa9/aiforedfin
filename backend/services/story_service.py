"""
AI FOR EDUCATION – Story Service
Generates narrative educational content with audio.
Supports multilingual generation with prosody.
"""

import logging
from typing import Optional
from services.gemini_service import generate_story
from services.tts_service import generate_story_audio, generate_multilingual_story_audio
from services.multilingual_story_engine import generate_multilingual_story as gen_multilingual

logger = logging.getLogger(__name__)


def create_story(topic: str, word_count: int = 400) -> dict:
    """
    Generate an educational story with audio narration (English).

    Args:
        topic: The topic to create a story about
        word_count: Approximate word count

    Returns:
        {
            "topic": str,
            "story_text": str,
            "audio_url": str
        }
    """
    logger.info(f"[Story] Creating story for topic: {topic} (word_count: {word_count})")

    # Generate story text
    story_text = generate_story(topic, word_count)
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


def create_multilingual_story(
    topic: str,
    language: str = "en",
    genre: str = "educational",
    age_group: str = "kids",
    word_count: int = 500,
    include_audio: bool = True
) -> dict:
    """
    Generate a multilingual educational story with prosody-enhanced audio.

    Args:
        topic: The educational topic
        language: Target language code
        genre: Story genre (adventure, mystery, science, etc.)
        age_group: Target audience age group
        word_count: Approximate word count
        include_audio: Whether to generate audio

    Returns:
        Story dictionary with text, audio, and metadata
    """
    logger.info(f"[Story] Creating multilingual story: {topic} ({language})")

    # Generate story with prosody markers
    story_data = gen_multilingual(
        topic=topic,
        language=language,
        genre=genre,
        age_group=age_group,
        word_count=word_count,
        include_prosody=True
    )

    # Generate audio if requested
    audio_url = None
    if include_audio:
        audio_path = generate_multilingual_story_audio(story_data)
        audio_filename = audio_path.split("/")[-1].split("\\")[-1]
        audio_url = f"/audio/{audio_filename}"
        logger.info(f"[Story] Multilingual audio generated: {audio_url}")

    return {
        "topic": topic,
        "story_text": story_data["story_text"],
        "language": story_data["language"],
        "language_name": story_data["language_name"],
        "genre": story_data["genre"],
        "age_group": story_data["age_group"],
        "word_count": story_data["word_count"],
        "voice": story_data["voice"],
        "audio_url": audio_url,
        "has_prosody": story_data["has_prosody"],
        "prosody": story_data.get("prosody"),
    }
