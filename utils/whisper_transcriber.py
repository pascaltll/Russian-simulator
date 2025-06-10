import whisper
import os
import logging

logger = logging.getLogger(__name__)

# Asegúrate de que el modelo de Whisper esté cargado aquí
# Si cargas el modelo globalmente, asegúrate de que se haga una vez
# Por ejemplo, puedes cargar 'base', 'small', 'medium', etc.
try:
    _model = whisper.load_model("base") # Puedes cambiar 'base' por el modelo que uses
    logger.info("Whisper model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading Whisper model: {e}", exc_info=True)
    _model = None # Set to None if loading fails

def transcribe_audio_with_whisper(audio_path: str) -> dict: # Changed return type to dict
    """
    Transcribes an audio file using the Whisper model and detects its language.

    Args:
        audio_path: The path to the audio file.

    Returns:
        A dictionary containing 'text' (transcription) and 'language' (detected language).
        Returns an error string if transcription fails.
    """
    if not os.path.exists(audio_path):
        return {"text": "Error: Audio file not found.", "language": "unknown"}
    
    if _model is None:
        return {"text": "Error: Whisper model not loaded.", "language": "unknown"}

    try:
        # Perform transcription and language detection
        # ¡CORRECCIÓN AQUÍ! Pasa fp16=False para decirle que use FP32
        result = _model.transcribe(audio_path, fp16=False)
        
        # The 'result' object from whisper.transcribe usually contains 'text' and 'language'
        transcription_text = result.get("text", "Transcription not available.")
        detected_language = result.get("language", "unknown")

        logger.info(f"Transcription successful. Detected language: {detected_language}")
        return {"text": transcription_text, "language": detected_language}

    except Exception as e:
        logger.error(f"Whisper transcription error: {e}", exc_info=True)
        return {"text": f"Whisper transcription error: {str(e)}", "language": "error"}