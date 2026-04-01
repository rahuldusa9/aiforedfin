"""
AI FOR EDUCATION – Services Package
"""

from services.recommendation_service import (
    get_user_recommendations,
    get_topic_recommendations_only,
    get_difficulty_recommendation_only,
    get_content_recommendation_only
)

# Prosody and Multilingual Services
from services.prosody_engine import (
    ProsodyEngine,
    get_prosody_engine,
    process_text_for_speech,
    EmotionType,
    ProsodySettings
)

from services.multilingual_voices import (
    get_voice_for_language,
    get_storyteller_voice,
    get_narrator_voice,
    get_available_languages,
    is_language_supported,
    MULTILINGUAL_VOICES
)

from services.multilingual_story_engine import (
    MultilingualStoryEngine,
    get_story_engine,
    generate_multilingual_story,
    get_supported_languages,
    StoryGenre,
    AgeGroup
)
