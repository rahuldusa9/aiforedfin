"""
AI FOR EDUCATION – Advanced Prosody Engine
SSML-based prosodic control for expressive, natural speech synthesis.
Supports emotional tonality, emphasis, pauses, and dramatic pacing.
"""

import re
import logging
from typing import Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EmotionType(Enum):
    """Emotional states that affect prosodic delivery."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    SUSPENSEFUL = "suspenseful"
    CALM = "calm"
    DRAMATIC = "dramatic"
    CURIOUS = "curious"
    SURPRISED = "surprised"
    THOUGHTFUL = "thoughtful"


class EmphasisLevel(Enum):
    """SSML emphasis levels."""
    REDUCED = "reduced"
    NONE = "none"
    MODERATE = "moderate"
    STRONG = "strong"


@dataclass
class ProsodySettings:
    """Prosodic parameters for speech synthesis."""
    rate: str = "+0%"       # Speech rate: -50% to +100%
    pitch: str = "+0Hz"     # Pitch adjustment: -50Hz to +50Hz
    volume: str = "+0%"     # Volume: -50% to +50%
    contour: Optional[str] = None  # Pitch contour for intonation


# -------------------------------------------------------
# Emotion-based Prosody Presets
# -------------------------------------------------------
EMOTION_PROSODY = {
    EmotionType.NEUTRAL: ProsodySettings(rate="+0%", pitch="+0Hz", volume="+0%"),
    EmotionType.HAPPY: ProsodySettings(rate="+10%", pitch="+15Hz", volume="+5%"),
    EmotionType.SAD: ProsodySettings(rate="-15%", pitch="-10Hz", volume="-10%"),
    EmotionType.EXCITED: ProsodySettings(rate="+20%", pitch="+20Hz", volume="+10%"),
    EmotionType.SUSPENSEFUL: ProsodySettings(rate="-20%", pitch="-5Hz", volume="-5%"),
    EmotionType.CALM: ProsodySettings(rate="-10%", pitch="-5Hz", volume="-5%"),
    EmotionType.DRAMATIC: ProsodySettings(rate="-15%", pitch="+10Hz", volume="+15%"),
    EmotionType.CURIOUS: ProsodySettings(rate="+5%", pitch="+10Hz", volume="+0%"),
    EmotionType.SURPRISED: ProsodySettings(rate="+15%", pitch="+25Hz", volume="+10%"),
    EmotionType.THOUGHTFUL: ProsodySettings(rate="-10%", pitch="+0Hz", volume="-5%"),
}

# -------------------------------------------------------
# Story Context Prosody Presets
# -------------------------------------------------------
STORY_CONTEXT_PROSODY = {
    "opening": ProsodySettings(rate="-5%", pitch="+5Hz", volume="+5%"),
    "rising_action": ProsodySettings(rate="+5%", pitch="+10Hz", volume="+5%"),
    "climax": ProsodySettings(rate="+15%", pitch="+15Hz", volume="+15%"),
    "falling_action": ProsodySettings(rate="-10%", pitch="-5Hz", volume="-5%"),
    "resolution": ProsodySettings(rate="-15%", pitch="-10Hz", volume="-10%"),
    "dialogue": ProsodySettings(rate="+5%", pitch="+10Hz", volume="+0%"),
    "narration": ProsodySettings(rate="-5%", pitch="+0Hz", volume="+0%"),
    "suspense": ProsodySettings(rate="-25%", pitch="-10Hz", volume="-10%"),
    "revelation": ProsodySettings(rate="+10%", pitch="+20Hz", volume="+10%"),
}

# -------------------------------------------------------
# Pause Durations (in milliseconds)
# -------------------------------------------------------
PAUSE_DURATIONS = {
    "micro": 150,       # Brief hesitation
    "short": 300,       # Comma pause
    "medium": 500,      # Sentence end
    "long": 800,        # Paragraph break
    "dramatic": 1200,   # For effect
    "scene_change": 1500,  # Scene transitions
}


class ProsodyEngine:
    """
    Advanced prosody engine for natural, expressive speech synthesis.
    Converts plain text into SSML with appropriate prosodic markers.
    """

    def __init__(self):
        self.emotion_patterns = self._compile_emotion_patterns()
        self.emphasis_patterns = self._compile_emphasis_patterns()

    def _compile_emotion_patterns(self) -> dict:
        """Compile regex patterns for emotion detection in text."""
        return {
            EmotionType.HAPPY: re.compile(
                r'\b(happy|joy|wonderful|amazing|fantastic|great|excellent|'
                r'delighted|thrilled|excited|brilliant|beautiful)\b', re.I
            ),
            EmotionType.SAD: re.compile(
                r'\b(sad|unfortunately|tragic|sorrow|grief|heartbreak|'
                r'disappointed|lost|lonely|crying|tears)\b', re.I
            ),
            EmotionType.EXCITED: re.compile(
                r'\b(wow|incredible|unbelievable|spectacular|extraordinary|'
                r'astonishing|rushed|quickly|suddenly)\b', re.I
            ),
            EmotionType.SUSPENSEFUL: re.compile(
                r'\b(mysterious|dark|shadow|unknown|danger|creeping|'
                r'silent|waiting|lurking|hidden)\b', re.I
            ),
            EmotionType.SURPRISED: re.compile(
                r'\b(surprised|shocked|gasped|stunned|amazed|'
                r'unexpected|sudden|what|impossible)\b', re.I
            ),
            EmotionType.CURIOUS: re.compile(
                r'\b(wonder|curious|question|mystery|puzzle|'
                r'discover|explore|investigate|why|how)\b', re.I
            ),
        }

    def _compile_emphasis_patterns(self) -> list:
        """Compile patterns for words that should be emphasized."""
        return [
            # Important educational terms
            (re.compile(r'\*\*([^*]+)\*\*'), EmphasisLevel.STRONG),  # **bold**
            (re.compile(r'\*([^*]+)\*'), EmphasisLevel.MODERATE),    # *italic*
            (re.compile(r'_([^_]+)_'), EmphasisLevel.MODERATE),      # _underscore_
            # Key words
            (re.compile(r'\b(important|critical|essential|key|crucial|'
                       r'remember|never|always|must|fundamental)\b', re.I),
             EmphasisLevel.STRONG),
            # Numbers and measurements
            (re.compile(r'\b(\d+(?:\.\d+)?(?:\s*(?:percent|%|degrees?|meters?|'
                       r'kilometers?|miles?|years?|days?|hours?))?)\b', re.I),
             EmphasisLevel.MODERATE),
        ]

    def detect_emotion(self, text: str) -> EmotionType:
        """Detect the dominant emotion in a text segment."""
        emotion_scores = {emotion: 0 for emotion in EmotionType}

        for emotion, pattern in self.emotion_patterns.items():
            matches = pattern.findall(text)
            emotion_scores[emotion] = len(matches)

        # Check for exclamation marks (excitement/surprise)
        if text.count('!') >= 2:
            emotion_scores[EmotionType.EXCITED] += 2
        elif text.count('!') == 1:
            emotion_scores[EmotionType.HAPPY] += 1

        # Check for question marks (curiosity)
        if '?' in text:
            emotion_scores[EmotionType.CURIOUS] += 1

        # Check for ellipsis (suspense/thoughtfulness)
        if '...' in text:
            emotion_scores[EmotionType.SUSPENSEFUL] += 1

        # Find dominant emotion
        max_score = max(emotion_scores.values())
        if max_score == 0:
            return EmotionType.NEUTRAL

        for emotion, score in emotion_scores.items():
            if score == max_score:
                return emotion

        return EmotionType.NEUTRAL

    def add_emphasis(self, text: str) -> str:
        """Add SSML emphasis tags to important words."""
        result = text

        for pattern, level in self.emphasis_patterns:
            if level == EmphasisLevel.STRONG:
                result = pattern.sub(
                    r'<emphasis level="strong">\1</emphasis>', result
                )
            elif level == EmphasisLevel.MODERATE:
                result = pattern.sub(
                    r'<emphasis level="moderate">\1</emphasis>', result
                )

        return result

    def add_pauses(self, text: str) -> str:
        """Insert natural pauses based on punctuation and context."""
        result = text

        # Scene transitions
        result = re.sub(
            r'\n---\n',
            f'\n<break time="{PAUSE_DURATIONS["scene_change"]}ms"/>\n',
            result
        )

        # Paragraph breaks
        result = re.sub(
            r'\n\n',
            f'\n<break time="{PAUSE_DURATIONS["long"]}ms"/>\n',
            result
        )

        # Ellipsis - dramatic pause
        result = re.sub(
            r'\.\.\.',
            f'<break time="{PAUSE_DURATIONS["dramatic"]}ms"/>',
            result
        )

        # Em dash - brief pause
        result = re.sub(
            r'—|--',
            f'<break time="{PAUSE_DURATIONS["short"]}ms"/>',
            result
        )

        # After colons before important info
        result = re.sub(
            r':(\s)',
            f':<break time="{PAUSE_DURATIONS["medium"]}ms"/>\\1',
            result
        )

        return result

    def wrap_dialogue(self, text: str) -> str:
        """Wrap dialogue in prosody tags for natural speech."""
        def dialogue_replacer(match):
            dialogue = match.group(1)
            # Detect emotion in dialogue
            emotion = self.detect_emotion(dialogue)
            prosody = EMOTION_PROSODY.get(emotion, EMOTION_PROSODY[EmotionType.NEUTRAL])

            return (f'<prosody rate="{prosody.rate}" pitch="{prosody.pitch}">'
                   f'"{dialogue}"</prosody>')

        # Match quoted dialogue
        result = re.sub(r'"([^"]+)"', dialogue_replacer, text)
        result = re.sub(r"'([^']+)'", dialogue_replacer, result)

        return result

    def apply_story_context_prosody(self, text: str, context: str = "narration") -> str:
        """Apply prosody based on story context (opening, climax, etc.)."""
        prosody = STORY_CONTEXT_PROSODY.get(context, STORY_CONTEXT_PROSODY["narration"])

        return (f'<prosody rate="{prosody.rate}" pitch="{prosody.pitch}" '
               f'volume="{prosody.volume}">{text}</prosody>')

    def generate_ssml(
        self,
        text: str,
        emotion: Optional[EmotionType] = None,
        add_emphasis: bool = True,
        add_pauses: bool = True,
        wrap_dialogue: bool = True,
        voice_name: Optional[str] = None,
    ) -> str:
        """
        Convert plain text to SSML with full prosodic markup.

        Args:
            text: Plain text to convert
            emotion: Override emotion detection with specific emotion
            add_emphasis: Add emphasis to important words
            add_pauses: Insert natural pauses
            wrap_dialogue: Apply prosody to quoted speech
            voice_name: Optional voice specification

        Returns:
            SSML-formatted string
        """
        result = text

        # Step 1: Add pauses
        if add_pauses:
            result = self.add_pauses(result)

        # Step 2: Wrap dialogue with emotion-aware prosody
        if wrap_dialogue:
            result = self.wrap_dialogue(result)

        # Step 3: Add emphasis to important words
        if add_emphasis:
            result = self.add_emphasis(result)

        # Step 4: Detect or apply overall emotion prosody
        if emotion is None:
            emotion = self.detect_emotion(text)

        prosody = EMOTION_PROSODY.get(emotion, EMOTION_PROSODY[EmotionType.NEUTRAL])

        # Build SSML document
        ssml_parts = ['<speak>']

        if voice_name:
            ssml_parts.append(f'<voice name="{voice_name}">')

        # Wrap in overall prosody
        ssml_parts.append(
            f'<prosody rate="{prosody.rate}" pitch="{prosody.pitch}" '
            f'volume="{prosody.volume}">'
        )
        ssml_parts.append(result)
        ssml_parts.append('</prosody>')

        if voice_name:
            ssml_parts.append('</voice>')

        ssml_parts.append('</speak>')

        return ''.join(ssml_parts)

    def process_story_for_narration(self, story_text: str) -> str:
        """
        Process a full story with intelligent prosodic markup.
        Analyzes story structure and applies appropriate prosody.
        """
        # Split into paragraphs
        paragraphs = story_text.strip().split('\n\n')
        processed_parts = []

        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue

            # Determine story context based on position
            position_ratio = i / max(len(paragraphs) - 1, 1)

            if i == 0:
                context = "opening"
            elif position_ratio < 0.3:
                context = "rising_action"
            elif position_ratio < 0.6:
                # Check for climax indicators
                if any(word in para.lower() for word in ['suddenly', 'then', 'finally', 'at last']):
                    context = "climax"
                else:
                    context = "rising_action"
            elif position_ratio < 0.8:
                context = "falling_action"
            else:
                context = "resolution"

            # Check for scene changes
            if para.startswith('---') or '---' in para:
                processed_parts.append(f'<break time="{PAUSE_DURATIONS["scene_change"]}ms"/>')
                para = para.replace('---', '').strip()

            # Detect if paragraph is mostly dialogue
            dialogue_ratio = len(re.findall(r'"[^"]+"', para)) / max(len(para.split()), 1)
            if dialogue_ratio > 0.3:
                context = "dialogue"

            # Process paragraph
            emotion = self.detect_emotion(para)
            processed_para = self.add_pauses(para)
            processed_para = self.wrap_dialogue(processed_para)
            processed_para = self.add_emphasis(processed_para)

            # Apply context-based prosody
            prosody = STORY_CONTEXT_PROSODY.get(context, STORY_CONTEXT_PROSODY["narration"])
            processed_para = (
                f'<prosody rate="{prosody.rate}" pitch="{prosody.pitch}" '
                f'volume="{prosody.volume}">{processed_para}</prosody>'
            )

            processed_parts.append(processed_para)

            # Add paragraph break
            processed_parts.append(f'<break time="{PAUSE_DURATIONS["long"]}ms"/>')

        # Build final SSML
        ssml = '<speak>' + ''.join(processed_parts) + '</speak>'

        logger.info(f"[Prosody] Processed story: {len(paragraphs)} paragraphs, SSML length: {len(ssml)}")

        return ssml

    def create_expressive_narration(
        self,
        text: str,
        style: str = "storytelling"
    ) -> tuple[str, ProsodySettings]:
        """
        Create expressive narration with style-appropriate prosody.

        Args:
            text: Text to narrate
            style: One of 'storytelling', 'educational', 'dramatic', 'calm'

        Returns:
            Tuple of (processed_ssml, base_prosody_settings)
        """
        style_settings = {
            "storytelling": ProsodySettings(rate="-10%", pitch="+5Hz", volume="+5%"),
            "educational": ProsodySettings(rate="-5%", pitch="+0Hz", volume="+0%"),
            "dramatic": ProsodySettings(rate="-15%", pitch="+10Hz", volume="+10%"),
            "calm": ProsodySettings(rate="-20%", pitch="-5Hz", volume="-10%"),
            "energetic": ProsodySettings(rate="+10%", pitch="+15Hz", volume="+10%"),
        }

        base_prosody = style_settings.get(style, style_settings["storytelling"])
        ssml = self.process_story_for_narration(text)

        return ssml, base_prosody


# Global engine instance
_prosody_engine = None


def get_prosody_engine() -> ProsodyEngine:
    """Get or create the global prosody engine instance."""
    global _prosody_engine
    if _prosody_engine is None:
        _prosody_engine = ProsodyEngine()
        logger.info("[Prosody] Engine initialized")
    return _prosody_engine


def process_text_for_speech(
    text: str,
    emotion: Optional[str] = None,
    style: str = "storytelling"
) -> tuple[str, ProsodySettings]:
    """
    Convenience function to process text for expressive speech.

    Args:
        text: Text to process
        emotion: Optional emotion override (happy, sad, excited, etc.)
        style: Narration style

    Returns:
        Tuple of (SSML text, prosody settings)
    """
    engine = get_prosody_engine()

    emotion_type = None
    if emotion:
        try:
            emotion_type = EmotionType(emotion.lower())
        except ValueError:
            pass

    if emotion_type:
        ssml = engine.generate_ssml(text, emotion=emotion_type)
        prosody = EMOTION_PROSODY.get(emotion_type, EMOTION_PROSODY[EmotionType.NEUTRAL])
        return ssml, prosody

    return engine.create_expressive_narration(text, style)
