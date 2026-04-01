"""
AI FOR EDUCATION – Multilingual Voice Configuration
Comprehensive voice support for 25+ languages with Edge TTS.
Includes voice selection by language, gender, and style.
"""

import logging
from dataclasses import dataclass
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class VoiceGender(Enum):
    """Voice gender options."""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class VoiceStyle(Enum):
    """Voice style/character options."""
    NARRATOR = "narrator"
    STORYTELLER = "storyteller"
    TEACHER = "teacher"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    CHILD = "child"
    ELDERLY = "elderly"


@dataclass
class VoiceProfile:
    """Complete voice profile with metadata."""
    voice_id: str           # Edge TTS voice identifier
    language_code: str      # ISO language code
    language_name: str      # Human-readable name
    gender: VoiceGender
    style: VoiceStyle
    description: str
    is_neural: bool = True
    supports_ssml: bool = True


# -------------------------------------------------------
# Comprehensive Multilingual Voice Database
# -------------------------------------------------------
MULTILINGUAL_VOICES = {
    # ============== ENGLISH ==============
    "en": {
        "default": "en-US-AriaNeural",
        "voices": [
            VoiceProfile("en-US-AriaNeural", "en-US", "English (US)", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Warm, expressive narrator"),
            VoiceProfile("en-US-JennyNeural", "en-US", "English (US)", VoiceGender.FEMALE, VoiceStyle.FRIENDLY, "Friendly conversational"),
            VoiceProfile("en-US-GuyNeural", "en-US", "English (US)", VoiceGender.MALE, VoiceStyle.PROFESSIONAL, "Professional male voice"),
            VoiceProfile("en-US-DavisNeural", "en-US", "English (US)", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Expressive storyteller"),
            VoiceProfile("en-US-AnaNeural", "en-US", "English (US)", VoiceGender.FEMALE, VoiceStyle.CHILD, "Young, friendly voice"),
            VoiceProfile("en-GB-SoniaNeural", "en-GB", "English (UK)", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "British narrator"),
            VoiceProfile("en-GB-RyanNeural", "en-GB", "English (UK)", VoiceGender.MALE, VoiceStyle.PROFESSIONAL, "British professional"),
            VoiceProfile("en-AU-NatashaNeural", "en-AU", "English (AU)", VoiceGender.FEMALE, VoiceStyle.FRIENDLY, "Australian friendly"),
            VoiceProfile("en-IN-NeerjaNeural", "en-IN", "English (India)", VoiceGender.FEMALE, VoiceStyle.TEACHER, "Indian English teacher"),
        ]
    },

    # ============== SPANISH ==============
    "es": {
        "default": "es-ES-ElviraNeural",
        "voices": [
            VoiceProfile("es-ES-ElviraNeural", "es-ES", "Spanish (Spain)", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Castilian narrator"),
            VoiceProfile("es-ES-AlvaroNeural", "es-ES", "Spanish (Spain)", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Spanish storyteller"),
            VoiceProfile("es-MX-DaliaNeural", "es-MX", "Spanish (Mexico)", VoiceGender.FEMALE, VoiceStyle.FRIENDLY, "Mexican friendly"),
            VoiceProfile("es-MX-JorgeNeural", "es-MX", "Spanish (Mexico)", VoiceGender.MALE, VoiceStyle.PROFESSIONAL, "Mexican professional"),
            VoiceProfile("es-AR-ElenaNeural", "es-AR", "Spanish (Argentina)", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Argentine narrator"),
            VoiceProfile("es-CO-SalomeNeural", "es-CO", "Spanish (Colombia)", VoiceGender.FEMALE, VoiceStyle.TEACHER, "Colombian teacher"),
        ]
    },

    # ============== FRENCH ==============
    "fr": {
        "default": "fr-FR-DeniseNeural",
        "voices": [
            VoiceProfile("fr-FR-DeniseNeural", "fr-FR", "French (France)", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "French narrator"),
            VoiceProfile("fr-FR-HenriNeural", "fr-FR", "French (France)", VoiceGender.MALE, VoiceStyle.STORYTELLER, "French storyteller"),
            VoiceProfile("fr-CA-SylvieNeural", "fr-CA", "French (Canada)", VoiceGender.FEMALE, VoiceStyle.FRIENDLY, "Québécois friendly"),
            VoiceProfile("fr-CA-JeanNeural", "fr-CA", "French (Canada)", VoiceGender.MALE, VoiceStyle.PROFESSIONAL, "Québécois professional"),
            VoiceProfile("fr-BE-CharlineNeural", "fr-BE", "French (Belgium)", VoiceGender.FEMALE, VoiceStyle.TEACHER, "Belgian French"),
        ]
    },

    # ============== GERMAN ==============
    "de": {
        "default": "de-DE-KatjaNeural",
        "voices": [
            VoiceProfile("de-DE-KatjaNeural", "de-DE", "German", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "German narrator"),
            VoiceProfile("de-DE-ConradNeural", "de-DE", "German", VoiceGender.MALE, VoiceStyle.STORYTELLER, "German storyteller"),
            VoiceProfile("de-DE-AmalaNeural", "de-DE", "German", VoiceGender.FEMALE, VoiceStyle.FRIENDLY, "Friendly German"),
            VoiceProfile("de-AT-IngridNeural", "de-AT", "German (Austria)", VoiceGender.FEMALE, VoiceStyle.TEACHER, "Austrian German"),
            VoiceProfile("de-CH-LeniNeural", "de-CH", "German (Swiss)", VoiceGender.FEMALE, VoiceStyle.PROFESSIONAL, "Swiss German"),
        ]
    },

    # ============== PORTUGUESE ==============
    "pt": {
        "default": "pt-BR-FranciscaNeural",
        "voices": [
            VoiceProfile("pt-BR-FranciscaNeural", "pt-BR", "Portuguese (Brazil)", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Brazilian narrator"),
            VoiceProfile("pt-BR-AntonioNeural", "pt-BR", "Portuguese (Brazil)", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Brazilian storyteller"),
            VoiceProfile("pt-PT-RaquelNeural", "pt-PT", "Portuguese (Portugal)", VoiceGender.FEMALE, VoiceStyle.TEACHER, "European Portuguese"),
            VoiceProfile("pt-PT-DuarteNeural", "pt-PT", "Portuguese (Portugal)", VoiceGender.MALE, VoiceStyle.PROFESSIONAL, "Portuguese professional"),
        ]
    },

    # ============== ITALIAN ==============
    "it": {
        "default": "it-IT-ElsaNeural",
        "voices": [
            VoiceProfile("it-IT-ElsaNeural", "it-IT", "Italian", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Italian narrator"),
            VoiceProfile("it-IT-IsabellaNeural", "it-IT", "Italian", VoiceGender.FEMALE, VoiceStyle.STORYTELLER, "Italian storyteller"),
            VoiceProfile("it-IT-DiegoNeural", "it-IT", "Italian", VoiceGender.MALE, VoiceStyle.PROFESSIONAL, "Italian professional"),
            VoiceProfile("it-IT-BenignoNeural", "it-IT", "Italian", VoiceGender.MALE, VoiceStyle.FRIENDLY, "Friendly Italian"),
        ]
    },

    # ============== CHINESE ==============
    "zh": {
        "default": "zh-CN-XiaoxiaoNeural",
        "voices": [
            VoiceProfile("zh-CN-XiaoxiaoNeural", "zh-CN", "Chinese (Mandarin)", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Mandarin narrator"),
            VoiceProfile("zh-CN-YunxiNeural", "zh-CN", "Chinese (Mandarin)", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Mandarin storyteller"),
            VoiceProfile("zh-CN-XiaohanNeural", "zh-CN", "Chinese (Mandarin)", VoiceGender.FEMALE, VoiceStyle.FRIENDLY, "Friendly Mandarin"),
            VoiceProfile("zh-CN-YunyangNeural", "zh-CN", "Chinese (Mandarin)", VoiceGender.MALE, VoiceStyle.PROFESSIONAL, "Professional Mandarin"),
            VoiceProfile("zh-TW-HsiaoChenNeural", "zh-TW", "Chinese (Taiwan)", VoiceGender.FEMALE, VoiceStyle.TEACHER, "Taiwanese Mandarin"),
            VoiceProfile("zh-HK-HiuGaaiNeural", "zh-HK", "Chinese (Cantonese)", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Cantonese narrator"),
        ]
    },

    # ============== JAPANESE ==============
    "ja": {
        "default": "ja-JP-NanamiNeural",
        "voices": [
            VoiceProfile("ja-JP-NanamiNeural", "ja-JP", "Japanese", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Japanese narrator"),
            VoiceProfile("ja-JP-KeitaNeural", "ja-JP", "Japanese", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Japanese storyteller"),
            VoiceProfile("ja-JP-AoiNeural", "ja-JP", "Japanese", VoiceGender.FEMALE, VoiceStyle.FRIENDLY, "Friendly Japanese"),
            VoiceProfile("ja-JP-DaichiNeural", "ja-JP", "Japanese", VoiceGender.MALE, VoiceStyle.PROFESSIONAL, "Professional Japanese"),
        ]
    },

    # ============== KOREAN ==============
    "ko": {
        "default": "ko-KR-SunHiNeural",
        "voices": [
            VoiceProfile("ko-KR-SunHiNeural", "ko-KR", "Korean", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Korean narrator"),
            VoiceProfile("ko-KR-InJoonNeural", "ko-KR", "Korean", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Korean storyteller"),
            VoiceProfile("ko-KR-YuJinNeural", "ko-KR", "Korean", VoiceGender.FEMALE, VoiceStyle.FRIENDLY, "Friendly Korean"),
            VoiceProfile("ko-KR-BongJinNeural", "ko-KR", "Korean", VoiceGender.MALE, VoiceStyle.PROFESSIONAL, "Professional Korean"),
        ]
    },

    # ============== HINDI ==============
    "hi": {
        "default": "hi-IN-SwaraNeural",
        "voices": [
            VoiceProfile("hi-IN-SwaraNeural", "hi-IN", "Hindi", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Hindi narrator"),
            VoiceProfile("hi-IN-MadhurNeural", "hi-IN", "Hindi", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Hindi storyteller"),
        ]
    },

    # ============== ARABIC ==============
    "ar": {
        "default": "ar-SA-ZariyahNeural",
        "voices": [
            VoiceProfile("ar-SA-ZariyahNeural", "ar-SA", "Arabic (Saudi)", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Arabic narrator"),
            VoiceProfile("ar-SA-HamedNeural", "ar-SA", "Arabic (Saudi)", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Arabic storyteller"),
            VoiceProfile("ar-EG-SalmaNeural", "ar-EG", "Arabic (Egypt)", VoiceGender.FEMALE, VoiceStyle.TEACHER, "Egyptian Arabic"),
            VoiceProfile("ar-AE-FatimaNeural", "ar-AE", "Arabic (UAE)", VoiceGender.FEMALE, VoiceStyle.PROFESSIONAL, "Emirati Arabic"),
        ]
    },

    # ============== RUSSIAN ==============
    "ru": {
        "default": "ru-RU-SvetlanaNeural",
        "voices": [
            VoiceProfile("ru-RU-SvetlanaNeural", "ru-RU", "Russian", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Russian narrator"),
            VoiceProfile("ru-RU-DmitryNeural", "ru-RU", "Russian", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Russian storyteller"),
            VoiceProfile("ru-RU-DariyaNeural", "ru-RU", "Russian", VoiceGender.FEMALE, VoiceStyle.FRIENDLY, "Friendly Russian"),
        ]
    },

    # ============== DUTCH ==============
    "nl": {
        "default": "nl-NL-ColetteNeural",
        "voices": [
            VoiceProfile("nl-NL-ColetteNeural", "nl-NL", "Dutch", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Dutch narrator"),
            VoiceProfile("nl-NL-MaartenNeural", "nl-NL", "Dutch", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Dutch storyteller"),
            VoiceProfile("nl-BE-ArnaudNeural", "nl-BE", "Dutch (Belgium)", VoiceGender.MALE, VoiceStyle.TEACHER, "Flemish Dutch"),
        ]
    },

    # ============== POLISH ==============
    "pl": {
        "default": "pl-PL-AgnieszkaNeural",
        "voices": [
            VoiceProfile("pl-PL-AgnieszkaNeural", "pl-PL", "Polish", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Polish narrator"),
            VoiceProfile("pl-PL-MarekNeural", "pl-PL", "Polish", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Polish storyteller"),
            VoiceProfile("pl-PL-ZofiaNeural", "pl-PL", "Polish", VoiceGender.FEMALE, VoiceStyle.FRIENDLY, "Friendly Polish"),
        ]
    },

    # ============== TURKISH ==============
    "tr": {
        "default": "tr-TR-EmelNeural",
        "voices": [
            VoiceProfile("tr-TR-EmelNeural", "tr-TR", "Turkish", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Turkish narrator"),
            VoiceProfile("tr-TR-AhmetNeural", "tr-TR", "Turkish", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Turkish storyteller"),
        ]
    },

    # ============== VIETNAMESE ==============
    "vi": {
        "default": "vi-VN-HoaiMyNeural",
        "voices": [
            VoiceProfile("vi-VN-HoaiMyNeural", "vi-VN", "Vietnamese", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Vietnamese narrator"),
            VoiceProfile("vi-VN-NamMinhNeural", "vi-VN", "Vietnamese", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Vietnamese storyteller"),
        ]
    },

    # ============== THAI ==============
    "th": {
        "default": "th-TH-PremwadeeNeural",
        "voices": [
            VoiceProfile("th-TH-PremwadeeNeural", "th-TH", "Thai", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Thai narrator"),
            VoiceProfile("th-TH-NiwatNeural", "th-TH", "Thai", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Thai storyteller"),
        ]
    },

    # ============== INDONESIAN ==============
    "id": {
        "default": "id-ID-GadisNeural",
        "voices": [
            VoiceProfile("id-ID-GadisNeural", "id-ID", "Indonesian", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Indonesian narrator"),
            VoiceProfile("id-ID-ArdiNeural", "id-ID", "Indonesian", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Indonesian storyteller"),
        ]
    },

    # ============== MALAY ==============
    "ms": {
        "default": "ms-MY-YasminNeural",
        "voices": [
            VoiceProfile("ms-MY-YasminNeural", "ms-MY", "Malay", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Malay narrator"),
            VoiceProfile("ms-MY-OsmanNeural", "ms-MY", "Malay", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Malay storyteller"),
        ]
    },

    # ============== SWEDISH ==============
    "sv": {
        "default": "sv-SE-SofieNeural",
        "voices": [
            VoiceProfile("sv-SE-SofieNeural", "sv-SE", "Swedish", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Swedish narrator"),
            VoiceProfile("sv-SE-MattiasNeural", "sv-SE", "Swedish", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Swedish storyteller"),
        ]
    },

    # ============== DANISH ==============
    "da": {
        "default": "da-DK-ChristelNeural",
        "voices": [
            VoiceProfile("da-DK-ChristelNeural", "da-DK", "Danish", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Danish narrator"),
            VoiceProfile("da-DK-JeppeNeural", "da-DK", "Danish", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Danish storyteller"),
        ]
    },

    # ============== NORWEGIAN ==============
    "no": {
        "default": "nb-NO-PernilleNeural",
        "voices": [
            VoiceProfile("nb-NO-PernilleNeural", "nb-NO", "Norwegian", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Norwegian narrator"),
            VoiceProfile("nb-NO-FinnNeural", "nb-NO", "Norwegian", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Norwegian storyteller"),
        ]
    },

    # ============== FINNISH ==============
    "fi": {
        "default": "fi-FI-NooraNeural",
        "voices": [
            VoiceProfile("fi-FI-NooraNeural", "fi-FI", "Finnish", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Finnish narrator"),
            VoiceProfile("fi-FI-HarriNeural", "fi-FI", "Finnish", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Finnish storyteller"),
        ]
    },

    # ============== GREEK ==============
    "el": {
        "default": "el-GR-AthinaNeural",
        "voices": [
            VoiceProfile("el-GR-AthinaNeural", "el-GR", "Greek", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Greek narrator"),
            VoiceProfile("el-GR-NestorNeural", "el-GR", "Greek", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Greek storyteller"),
        ]
    },

    # ============== HEBREW ==============
    "he": {
        "default": "he-IL-HilaNeural",
        "voices": [
            VoiceProfile("he-IL-HilaNeural", "he-IL", "Hebrew", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Hebrew narrator"),
            VoiceProfile("he-IL-AvriNeural", "he-IL", "Hebrew", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Hebrew storyteller"),
        ]
    },

    # ============== CZECH ==============
    "cs": {
        "default": "cs-CZ-VlastaNeural",
        "voices": [
            VoiceProfile("cs-CZ-VlastaNeural", "cs-CZ", "Czech", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Czech narrator"),
            VoiceProfile("cs-CZ-AntoninNeural", "cs-CZ", "Czech", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Czech storyteller"),
        ]
    },

    # ============== HUNGARIAN ==============
    "hu": {
        "default": "hu-HU-NoemiNeural",
        "voices": [
            VoiceProfile("hu-HU-NoemiNeural", "hu-HU", "Hungarian", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Hungarian narrator"),
            VoiceProfile("hu-HU-TamasNeural", "hu-HU", "Hungarian", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Hungarian storyteller"),
        ]
    },

    # ============== ROMANIAN ==============
    "ro": {
        "default": "ro-RO-AlinaNeural",
        "voices": [
            VoiceProfile("ro-RO-AlinaNeural", "ro-RO", "Romanian", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Romanian narrator"),
            VoiceProfile("ro-RO-EmilNeural", "ro-RO", "Romanian", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Romanian storyteller"),
        ]
    },

    # ============== UKRAINIAN ==============
    "uk": {
        "default": "uk-UA-PolinaNeural",
        "voices": [
            VoiceProfile("uk-UA-PolinaNeural", "uk-UA", "Ukrainian", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Ukrainian narrator"),
            VoiceProfile("uk-UA-OstapNeural", "uk-UA", "Ukrainian", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Ukrainian storyteller"),
        ]
    },

    # ============== TAMIL ==============
    "ta": {
        "default": "ta-IN-PallaviNeural",
        "voices": [
            VoiceProfile("ta-IN-PallaviNeural", "ta-IN", "Tamil", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Tamil narrator"),
            VoiceProfile("ta-IN-ValluvarNeural", "ta-IN", "Tamil", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Tamil storyteller"),
        ]
    },

    # ============== TELUGU ==============
    "te": {
        "default": "te-IN-ShrutiNeural",
        "voices": [
            VoiceProfile("te-IN-ShrutiNeural", "te-IN", "Telugu", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Telugu narrator"),
            VoiceProfile("te-IN-MohanNeural", "te-IN", "Telugu", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Telugu storyteller"),
        ]
    },

    # ============== BENGALI ==============
    "bn": {
        "default": "bn-IN-TanishaaNeural",
        "voices": [
            VoiceProfile("bn-IN-TanishaaNeural", "bn-IN", "Bengali", VoiceGender.FEMALE, VoiceStyle.NARRATOR, "Bengali narrator"),
            VoiceProfile("bn-IN-BashkarNeural", "bn-IN", "Bengali", VoiceGender.MALE, VoiceStyle.STORYTELLER, "Bengali storyteller"),
        ]
    },
}

# Language name mappings for user-friendly display
LANGUAGE_NAMES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "pt": "Portuguese",
    "it": "Italian",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "hi": "Hindi",
    "ar": "Arabic",
    "ru": "Russian",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "ms": "Malay",
    "sv": "Swedish",
    "da": "Danish",
    "no": "Norwegian",
    "fi": "Finnish",
    "el": "Greek",
    "he": "Hebrew",
    "cs": "Czech",
    "hu": "Hungarian",
    "ro": "Romanian",
    "uk": "Ukrainian",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
}


def get_voice_for_language(
    language_code: str,
    gender: Optional[VoiceGender] = None,
    style: Optional[VoiceStyle] = None
) -> str:
    """
    Get the best matching voice for a language.

    Args:
        language_code: ISO language code (e.g., 'en', 'es', 'fr')
        gender: Preferred gender (optional)
        style: Preferred style (optional)

    Returns:
        Edge TTS voice identifier
    """
    # Normalize language code
    lang = language_code.lower().split('-')[0]

    if lang not in MULTILINGUAL_VOICES:
        logger.warning(f"[Voice] Language '{lang}' not supported, falling back to English")
        lang = "en"

    lang_config = MULTILINGUAL_VOICES[lang]
    voices = lang_config["voices"]

    # Filter by gender if specified
    if gender:
        gender_filtered = [v for v in voices if v.gender == gender]
        if gender_filtered:
            voices = gender_filtered

    # Filter by style if specified
    if style:
        style_filtered = [v for v in voices if v.style == style]
        if style_filtered:
            voices = style_filtered

    # Return best match or default
    if voices:
        return voices[0].voice_id

    return lang_config["default"]


def get_narrator_voice(language_code: str) -> str:
    """Get the narrator voice for a language (best for storytelling)."""
    return get_voice_for_language(language_code, style=VoiceStyle.NARRATOR)


def get_storyteller_voice(language_code: str) -> str:
    """Get the storyteller voice for a language (expressive for stories)."""
    return get_voice_for_language(language_code, style=VoiceStyle.STORYTELLER)


def get_teacher_voice(language_code: str) -> str:
    """Get the teacher voice for a language (clear for education)."""
    voice = get_voice_for_language(language_code, style=VoiceStyle.TEACHER)
    # Fallback to narrator if no teacher voice
    if not voice:
        voice = get_voice_for_language(language_code, style=VoiceStyle.NARRATOR)
    return voice


def get_available_languages() -> list[dict]:
    """
    Get list of all available languages with their details.

    Returns:
        List of {code, name, voice_count}
    """
    return [
        {
            "code": code,
            "name": LANGUAGE_NAMES.get(code, code.upper()),
            "voice_count": len(MULTILINGUAL_VOICES[code]["voices"]),
            "voices": [
                {
                    "id": v.voice_id,
                    "gender": v.gender.value,
                    "style": v.style.value,
                    "description": v.description
                }
                for v in MULTILINGUAL_VOICES[code]["voices"]
            ]
        }
        for code in sorted(MULTILINGUAL_VOICES.keys())
    ]


def get_voices_for_language(language_code: str) -> list[VoiceProfile]:
    """
    Get all available voices for a specific language.

    Args:
        language_code: ISO language code

    Returns:
        List of VoiceProfile objects
    """
    lang = language_code.lower().split('-')[0]
    if lang not in MULTILINGUAL_VOICES:
        return []
    return MULTILINGUAL_VOICES[lang]["voices"]


def is_language_supported(language_code: str) -> bool:
    """Check if a language is supported."""
    lang = language_code.lower().split('-')[0]
    return lang in MULTILINGUAL_VOICES


def detect_language_from_text(text: str) -> str:
    """
    Simple language detection based on character patterns.
    For production, consider using langdetect or similar library.

    Args:
        text: Input text

    Returns:
        Detected language code (defaults to 'en')
    """
    # Character range detection
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return 'zh'  # Chinese
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text):
        return 'ja'  # Japanese
    if any('\uac00' <= c <= '\ud7af' for c in text):
        return 'ko'  # Korean
    if any('\u0600' <= c <= '\u06ff' for c in text):
        return 'ar'  # Arabic
    if any('\u0590' <= c <= '\u05ff' for c in text):
        return 'he'  # Hebrew
    if any('\u0900' <= c <= '\u097f' for c in text):
        return 'hi'  # Hindi
    if any('\u0e00' <= c <= '\u0e7f' for c in text):
        return 'th'  # Thai
    if any('\u0b80' <= c <= '\u0bff' for c in text):
        return 'ta'  # Tamil
    if any('\u0c00' <= c <= '\u0c7f' for c in text):
        return 'te'  # Telugu
    if any('\u0980' <= c <= '\u09ff' for c in text):
        return 'bn'  # Bengali
    if any('\u0400' <= c <= '\u04ff' for c in text):
        # Could be Russian or Ukrainian - default to Russian
        return 'ru'
    if any('\u0370' <= c <= '\u03ff' for c in text):
        return 'el'  # Greek

    # Default to English for Latin-based scripts
    return 'en'
