"""
AI FOR EDUCATION – Text-to-Speech Service
Uses Edge TTS (primary) with gTTS fallback for speech generation,
and PyDub for audio refinement.
"""

import logging
import uuid
from pathlib import Path

import edge_tts
from pydub import AudioSegment
from config import AUDIO_OUTPUT_DIR

logger = logging.getLogger(__name__)

# -------------------------------------------------------
# Voice Configuration (Edge TTS voices)
# -------------------------------------------------------
VOICES = {
    "Host": "en-US-GuyNeural",
    "Expert": "en-US-JennyNeural",
    "narrator": "en-US-AriaNeural",
    "default": "en-US-AriaNeural",
}


def _generate_with_edge_tts(text: str, voice: str, output_path: str) -> str:
    """
    Generate speech using Edge TTS v7+ synchronous API.
    
    Args:
        text: Text to convert to speech
        voice: Edge TTS voice name
        output_path: Output file path
    
    Returns:
        Path to generated audio file
    """
    communicate = edge_tts.Communicate(text, voice)
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


def generate_speech(text: str, voice: str = "default", filename: str = None) -> str:
    """
    Generate speech audio with Edge TTS (primary) and gTTS (fallback).
    
    Args:
        text: Text to speak
        voice: Voice key or full voice name
        filename: Optional filename (auto-generated if None)
    
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
        _generate_with_edge_tts(text, voice_name, output_path)
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


def generate_podcast_audio(script: list[dict]) -> str:
    """
    Generate a full podcast MP3 from a script with multiple speakers.
    
    Args:
        script: List of {"speaker": "...", "text": "..."} entries
    
    Returns:
        Path to the combined podcast MP3
    """
    segments = []
    temp_files = []

    for i, entry in enumerate(script):
        speaker = entry.get("speaker", "default")
        text = entry.get("text", "")
        if not text.strip():
            continue

        # Generate individual segment
        temp_filename = f"podcast_seg_{uuid.uuid4().hex[:8]}_{i}.mp3"
        temp_path = generate_speech(text, voice=speaker, filename=temp_filename)
        temp_files.append(temp_path)

        try:
            segment = AudioSegment.from_file(temp_path)
            segments.append(segment)

            # Add a small pause between speakers
            pause = AudioSegment.silent(duration=400)
            segments.append(pause)
        except Exception as e:
            logger.warning(f"[TTS] Could not load segment {i}: {e}")

    if not segments:
        raise ValueError("No audio segments were generated.")

    # Combine all segments
    combined = segments[0]
    for seg in segments[1:]:
        combined += seg

    # Refine combined audio
    output_filename = f"podcast_{uuid.uuid4().hex[:12]}.mp3"
    output_path = str(Path(AUDIO_OUTPUT_DIR) / output_filename)
    combined.export(output_path, format="mp3", bitrate="192k")

    # Refine final output
    refine_audio(output_path)

    # Clean up temp files
    for temp_file in temp_files:
        try:
            Path(temp_file).unlink(missing_ok=True)
        except Exception:
            pass

    logger.info(f"[TTS] Podcast audio generated: {output_path}")
    return output_path


def generate_story_audio(text: str) -> str:
    """
    Generate narrated story audio.
    
    Args:
        text: Story text to narrate
    
    Returns:
        Path to the story MP3
    """
    filename = f"story_{uuid.uuid4().hex[:12]}.mp3"
    path = generate_speech(text, voice="narrator", filename=filename)
    refine_audio(path)
    return path
