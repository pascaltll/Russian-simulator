# services/vocabulary_nlp_service.py
import logging
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger(__name__)

class VocabularyNLPService:
    _instance = None
    _translation_pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VocabularyNLPService, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance

    def _load_models(self):
        try:
            logger.info("Attempting to load Helsinki-NLP/opus-mt-ru-es model...")
            self._translation_pipeline = pipeline(
                "translation", model="Helsinki-NLP/opus-mt-ru-es"
            )
            logger.info("Helsinki-NLP/opus-mt-ru-es model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading Helsinki-NLP/opus-mt-ru-es model: {e}")
            self._translation_pipeline = None

    def suggest_translation_and_comment(self, russian_word: str, target_language: str):
        # Default response if model not loaded or error occurs
        default_response = {
            "russian_word": russian_word,
            "suggested_translation": f"No translation available for {target_language}.",
            "suggested_example_sentence": "Translation service currently unavailable."
        }

        if not self._translation_pipeline:
            logger.warning("Translation pipeline not loaded. Cannot suggest translation.")
            return default_response

        try:
            translated_result = self._translation_pipeline(russian_word)
            translation = translated_result[0]['translation_text']

            # Generate a simple example sentence. You might want more sophisticated logic here.
            example_sentence = f"Ejemplo: '{translation}'."

            return {
                "russian_word": russian_word,
                "suggested_translation": translation,
                "suggested_example_sentence": example_sentence
            }
        except Exception as e:
            logger.error(f"Error during translation for '{russian_word}': {e}")
            return default_response