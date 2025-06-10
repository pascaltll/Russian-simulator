"""
Utility module for audio transcription using the Whisper model.

This module handles loading the Whisper model and transcribing audio files,
including language detection.
"""

import logging
import os

import whisper

logger = logging.getLogger(__name__)

WHISPER_MODEL = None

try:
    logger.info("Attempting to load Whisper 'base' model...")
    WHISPER_MODEL = whisper.load_model("base")
    logger.info("Whisper 'base' model loaded successfully.")
except (OSError, RuntimeError) as exc:
    logger.error("Error loading Whisper model: %s", exc, exc_info=True)
    WHISPER_MODEL = None


def transcribe_audio_with_whisper(audio_path: str) -> dict:
    """
    Transcribes an audio file using the Whisper model and detects its language.

    Args:
        audio_path (str): The path to the audio file.

    Returns:
        dict: A dictionary containing 'text' (transcription) and 'language' (detected language).
              Returns an error dictionary if transcription fails.
    """
    if not os.path.exists(audio_path):
        logger.error("Audio file not found at path: %s", audio_path)
        return {"text": "Error: Audio file not found.", "language": "unknown"}

    if WHISPER_MODEL is None:
        logger.error("Whisper model not loaded, cannot perform transcription.")
        return {"text": "Error: Whisper model not loaded.", "language": "unknown"}

    try:
        result = WHISPER_MODEL.transcribe(audio_path, fp16=False)
        transcription_text = result.get("text", "Transcription not available.")
        detected_language = result.get("language", "unknown")

        logger.info("Transcription successful. Detected language: %s", detected_language)
        return {"text": transcription_text, "language": detected_language}

    except (ValueError, OSError, RuntimeError) as exc:
        logger.error("Whisper transcription error: %s", exc, exc_info=True)
        return {"text": f"Whisper transcription error: {exc}", "language": "error"}
