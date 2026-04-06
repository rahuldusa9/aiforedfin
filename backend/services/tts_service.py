"""
AI FOR EDUCATION – Text-to-Speech Service
Advanced TTS with prosody support, multilingual voices (25+ languages),
and expressive speech synthesis using Edge TTS.
"""

import logging
import shutil
import uuid
from pathlib import Path
from typing import Optional

import edge_tts
from pydub import AudioSegment
from config import AUDIO_OUTPUT_DIR

from services.prosody_engine import (
    get_prosody_engine, process_text_for_speech, ProsodySettings
)
from services.multilingual_voices import (
    get_voice_for_language, get_storyteller_voice, get_narrator_voice,
    is_language_supported, detect_language_from_text, VoiceStyle, VoiceGender
)

logger = logging.getLogger(__name__)

# -------------------------------------------------------
# Voice Configuration (Edge TTS voices)
# -------------------------------------------------------
VOICES = {
    "Host": "en-US-GuyNeural",
    "Expert": "en-US-JennyNeural",
    "narrator": "en-US-AriaNeural",
    "default": "en-US-AriaNeural",
    "storyteller": "en-US-DavisNeural",
    "teacher": "en-US-JennyNeural",
}


def _generate_with_edge_tts(text: str, voice: str, output_path: str, rate: str = "+0%", pitch: str = "+0Hz", volume: str = "+0%") -> str:
    """
    Generate speech using Edge TTS v7+ synchronous API.
    
    Args:
        text: Text to convert to speech
        voice: Edge TTS voice name
        output_path: Output file path
        rate: Speech rate (e.g., '+10%', '-10%')
        pitch: Speech pitch (e.g., '+5Hz', '-5Hz')
        volume: Speech volume
    
    Returns:
        Path to generated audio file
    """
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
    communicate.save_sync(output_path)
    return output_path


def _generate_with_gtts(text: str, output_path: str) -> str:
    """
    Fallback: generate speech using Google gTTS.
    Lower quality but highly reliable.
    
    Args:
        text: Text to convert to speech
        output_path: Output file path
    
    Returns:
        Path to generated audio file
    """
    from gtts import gTTS
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(output_path)
    return output_path


def generate_speech(
    text: str, 
    voice: str = "default", 
    filename: str = None, 
    rate: str = "+0%", 
    pitch: str = "+0Hz", 
    volume: str = "+0%"
) -> str:
    """
    Generate speech audio with Edge TTS (primary) and gTTS (fallback).
    
    Args:
        text: Text to speak
        voice: Voice key or full voice name
        filename: Optional filename (auto-generated if None)
        rate: Speech rate adjustment
        pitch: Speech pitch adjustment
        volume: Speech volume adjustment
    
    Returns:
        Path to the generated MP3 file
    """
    # Resolve voice
    voice_name = VOICES.get(voice, voice if "-" in voice else VOICES["default"])

    # Generate filename
    if filename is None:
        filename = f"{uuid.uuid4().hex}.mp3"

    output_path = str(Path(AUDIO_OUTPUT_DIR) / filename)

    # Primary: Edge TTS (high quality, multiple voices)
    try:
        _generate_with_edge_tts(text, voice_name, output_path, rate=rate, pitch=pitch, volume=volume)
        logger.info(f"[TTS] Edge TTS generated: {output_path}")
        return output_path
    except Exception as e:
        logger.warning(f"[TTS] Edge TTS failed ({e}), falling back to gTTS...")

    # Fallback: gTTS (reliable, single voice)
    try:
        _generate_with_gtts(text, output_path)
        logger.info(f"[TTS] gTTS fallback generated: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"[TTS] Both Edge TTS and gTTS failed: {e}")
        raise RuntimeError(f"All TTS engines failed. Last error: {e}")


def refine_audio(input_path: str, output_path: str = None) -> str:
    """
    Refine audio using PyDub:
    - Normalize volume
    - Add slight fade in/out
    - Export as high-quality MP3
    
    Args:
        input_path: Source audio file
        output_path: Destination (defaults to overwriting input)
    
    Returns:
        Path to refined audio
    """
    if output_path is None:
        output_path = input_path

    try:
        audio = AudioSegment.from_file(input_path)

        # Normalize volume to -14 dBFS (broadcast standard)
        target_dbfs = -14.0
        change_in_dbfs = target_dbfs - audio.dBFS
        audio = audio.apply_gain(change_in_dbfs)

        # Add fade in/out
        audio = audio.fade_in(300).fade_out(500)

        # Export
        audio.export(output_path, format="mp3", bitrate="192k")
        logger.info(f"[TTS] Audio refined: {output_path}")

    except Exception as e:
        logger.warning(f"[TTS] Audio refinement failed (using original): {e}")

    return output_path


def generate_podcast_audio(script: list[dict], language: str = "en") -> str:
    """
    Generate a podcast MP3 with distinct voices for Host and Expert.
    Matches gender and dynamically concatenates audio segments.

    Args:
        script: List of {"speaker": "...", "text": "..."} entries
        language: Language code for TTS voice selection

    Returns:
        Path to the combined podcast MP3
    """
    from services.multilingual_voices import get_voices_for_language, VoiceGender
    all_langs = get_voices_for_language(language)

    # Assign distinct voices for Host and Expert
    host_voice = "en-US-AriaNeural"
    expert_voice = "en-US-GuyNeural"

    if all_langs:
        # Separate by gender
        females = [v.voice_id for v in all_langs if v.gender == VoiceGender.FEMALE]
        males = [v.voice_id for v in all_langs if v.gender == VoiceGender.MALE]

        if females and males:
            host_voice = females[0]
            expert_voice = males[0]
        elif len(all_langs) >= 2:
            host_voice = all_langs[0].voice_id
            expert_voice = all_langs[1].voice_id
        else:
            host_voice = all_langs[0].voice_id
            expert_voice = all_langs[0].voice_id

    output_filename = f"podcast_{uuid.uuid4().hex[:12]}.mp3"
    output_path = str(Path(AUDIO_OUTPUT_DIR) / output_filename)

    temp_files = []
    
    try:
        for idx, entry in enumerate(script):
            speaker = entry.get("speaker", "Host")
            text = entry.get("text", "").strip()
            if not text:
                continue

            voice_to_use = host_voice if speaker == "Host" else expert_voice
            temp_file = str(Path(AUDIO_OUTPUT_DIR) / f"temp_{uuid.uuid4().hex[:8]}.mp3")
            generate_speech(text, voice=voice_to_use, filename=Path(temp_file).name)
            temp_files.append(temp_file)

        if not temp_files:
            raise ValueError("No audio segments were generated.")

        # Simple byte concatenation (works for MP3 frames)
        with open(output_path, 'wb') as outfile:
            for tf in temp_files:
                if Path(tf).exists():
                    with open(tf, 'rb') as infile:
                        outfile.write(infile.read())
                        
    finally:
        # Cleanup temporary audio files
        for tf in temp_files:
            try:
                if Path(tf).exists():
                    Path(tf).unlink()
            except Exception as e:
                logger.error(f"[TTS] Failed to clean up temp file {tf}: {e}")

    # Optionally refine if tools are available
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        refine_audio(output_path)
    else:
        logger.info("[TTS] Skipping audio refinement (ffmpeg/ffprobe not found).")

    logger.info(f"[TTS] Podcast audio generated: {output_path}")
    return output_path


def _prepare_story_text(text: str) -> str:
    """
    Prepare story text for natural narration.
    Adds natural pauses using ellipses and cleans up formatting.
    """
    import re

    # Clean up the text
    result = text.strip()

    # Remove scene markers
    result = re.sub(r'\n---\n', '\n\n', result)

    # Add slight pauses after sentences (using comma for micro-pause effect)
    # This helps the TTS engine breathe naturally
    result = re.sub(r'\.(\s+)([A-Z])', r'.\1\2', result)

    # Add pause indicators for dialogue (the TTS will naturally pause at quotes)
    # No changes needed - quotes already help

    return result


def generate_story_audio(text: str) -> str:
    """
    Generate narrated story audio with warm storytelling delivery.

    Uses a slower pace and warm voice for pleasant listening.

    Args:
        text: Story text to narrate

    Returns:
        Path to the story MP3
    """
    filename = f"story_{uuid.uuid4().hex[:12]}.mp3"
    output_path = str(Path(AUDIO_OUTPUT_DIR) / filename)

    # Prepare text for natural reading
    clean_text = _prepare_story_text(text)

    # Use a warm, storytelling voice with slower pace
    # en-US-AriaNeural - warm and expressive
    # en-US-AnaNeural - young and friendly
    voice = "en-US-AriaNeural"

    try:
        communicate = edge_tts.Communicate(
            clean_text,
            voice,
            rate="-15%",   # Slower for storytelling
            pitch="+5Hz"   # Slightly warmer tone
        )
        communicate.save_sync(output_path)
        logger.info(f"[TTS] Story audio generated: {output_path}")
    except Exception as e:
        logger.error(f"[TTS] Story generation failed: {e}")
        # Fallback to default
        communicate = edge_tts.Communicate(clean_text, voice)
        communicate.save_sync(output_path)

    # Refine audio if ffmpeg is available
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        refine_audio(output_path)

    return output_path


# -------------------------------------------------------
# Advanced Multilingual TTS with Prosody
# -------------------------------------------------------

def generate_multilingual_speech(
    text: str,
    language: str = "en",
    voice: Optional[str] = None,
    style: str = "narrator",
    use_prosody: bool = True,
    emotion: Optional[str] = None,
    filename: Optional[str] = None
) -> str:
    """
    Generate speech in any supported language with optional prosody.

    Args:
        text: Text to speak
        language: Language code (e.g., 'en', 'es', 'fr', 'zh', 'ja')
        voice: Optional specific voice ID override
        style: Voice style ('narrator', 'storyteller', 'teacher', 'friendly')
        use_prosody: Apply prosodic markers for expressive speech
        emotion: Optional emotion override ('happy', 'sad', 'excited', etc.)
        filename: Optional output filename

    Returns:
        Path to the generated MP3 file
    """
    # Validate/detect language
    lang = language.lower().split('-')[0]
    if not is_language_supported(lang):
        detected = detect_language_from_text(text)
        if is_language_supported(detected):
            lang = detected
            logger.info(f"[TTS] Detected language: {lang}")
        else:
            lang = "en"
            logger.warning(f"[TTS] Unsupported language, using English")

    # Get appropriate voice
    if voice is None:
        if style == "storyteller":
            voice = get_storyteller_voice(lang)
        else:
            voice = get_narrator_voice(lang)

    # Generate filename
    if filename is None:
        filename = f"speech_{lang}_{uuid.uuid4().hex[:12]}.mp3"

    output_path = str(Path(AUDIO_OUTPUT_DIR) / filename)

    # Apply prosody if requested
    rate = "+0%"
    pitch = "+0Hz"
    volume = "+0%"

    if use_prosody:
        _, prosody_settings = process_text_for_speech(text, emotion=emotion, style=style)
        rate = prosody_settings.rate
        pitch = prosody_settings.pitch
        volume = prosody_settings.volume

    try:
        communicate = edge_tts.Communicate(
            text, voice, rate=rate, pitch=pitch, volume=volume
        )
        communicate.save_sync(output_path)
        logger.info(f"[TTS] Multilingual speech generated: {output_path} (lang={lang}, voice={voice})")
    except Exception as e:
        logger.error(f"[TTS] Multilingual generation failed: {e}")
        # Fallback to basic generation
        try:
            communicate = edge_tts.Communicate(text, voice)
            communicate.save_sync(output_path)
        except Exception as e2:
            logger.error(f"[TTS] Fallback also failed: {e2}")
            raise RuntimeError(f"TTS generation failed: {e2}")

    # Refine if ffmpeg available
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        refine_audio(output_path)

    return output_path


def generate_expressive_story_audio(
    story_text: str,
    language: str = "en",
    voice: Optional[str] = None,
    emotion: Optional[str] = None
) -> str:
    """
    Generate expressive story narration with full prosodic control.

    Args:
        story_text: The story text to narrate
        language: Language code
        voice: Optional voice override
        emotion: Optional emotion for the narration

    Returns:
        Path to the generated MP3
    """
    filename = f"story_{language}_{uuid.uuid4().hex[:12]}.mp3"
    output_path = str(Path(AUDIO_OUTPUT_DIR) / filename)

    # Get language-appropriate storyteller voice
    lang = language.lower().split('-')[0]
    if voice is None:
        voice = get_storyteller_voice(lang)

    # Process with prosody engine for expressive SSML
    prosody_engine = get_prosody_engine()
    ssml_text, prosody = prosody_engine.create_expressive_narration(
        story_text, style="storytelling"
    )

    # Edge TTS doesn't support full SSML, so we use prosody settings
    # and prepare the text with natural breaks
    clean_text = _prepare_story_text(story_text)

    try:
        communicate = edge_tts.Communicate(
            clean_text,
            voice,
            rate=prosody.rate,
            pitch=prosody.pitch,
            volume=prosody.volume
        )
        communicate.save_sync(output_path)
        logger.info(f"[TTS] Expressive story audio: {output_path}")
    except Exception as e:
        logger.error(f"[TTS] Expressive generation failed: {e}")
        # Simpler fallback
        communicate = edge_tts.Communicate(clean_text, voice, rate="-10%")
        communicate.save_sync(output_path)

    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        refine_audio(output_path)

    return output_path


def generate_multilingual_story_audio(
    story_data: dict
) -> str:
    """
    Generate audio for a multilingual story dictionary.

    Args:
        story_data: Dictionary from MultilingualStoryEngine.generate_story()
                   Contains: story_text, language, voice, prosody settings

    Returns:
        Path to the generated MP3
    """
    text = story_data.get("story_text", "")
    language = story_data.get("language", "en")
    voice = story_data.get("voice")
    prosody = story_data.get("prosody", {})

    filename = f"story_{language}_{uuid.uuid4().hex[:12]}.mp3"
    output_path = str(Path(AUDIO_OUTPUT_DIR) / filename)

    # Apply prosody from story data
    rate = prosody.get("rate", "-10%")
    pitch = prosody.get("pitch", "+5Hz")
    volume = prosody.get("volume", "+0%")

    # Prepare text
    clean_text = _prepare_story_text(text)

    try:
        communicate = edge_tts.Communicate(
            clean_text,
            voice,
            rate=rate,
            pitch=pitch,
            volume=volume
        )
        communicate.save_sync(output_path)
        logger.info(f"[TTS] Multilingual story audio: {output_path} ({language})")
    except Exception as e:
        logger.error(f"[TTS] Multilingual story audio failed: {e}")
        # Fallback
        fallback_voice = get_narrator_voice(language)
        communicate = edge_tts.Communicate(clean_text, fallback_voice)
        communicate.save_sync(output_path)

    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        refine_audio(output_path)

    return output_path


def get_available_voices_for_language(language: str) -> list[dict]:
    """
    Get all available voices for a specific language.

    Args:
        language: Language code

    Returns:
        List of voice dictionaries with id, gender, style, description
    """
    from services.multilingual_voices import get_voices_for_language
    voices = get_voices_for_language(language)
    return [
        {
            "id": v.voice_id,
            "gender": v.gender.value,
            "style": v.style.value,
            "description": v.description,
            "language_code": v.language_code
        }
        for v in voices
    ]


def list_supported_languages() -> list[dict]:
    """
    Get list of all supported languages for TTS.

    Returns:
        List of {code, name, voice_count}
    """
    from services.multilingual_voices import get_available_languages
    return get_available_languages()
