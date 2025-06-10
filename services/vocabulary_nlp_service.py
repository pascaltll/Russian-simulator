"""
NLP service for vocabulary-related tasks.

Provides a singleton service for suggesting translations and example sentences
for Russian words using pre-trained NLP models from Helsinki-NLP.
"""

# Group 1: Standard libraries
import logging
from typing import Dict, Any

# Group 2: Third-party libraries
from transformers import pipeline, Pipeline

logger = logging.getLogger(__name__)


class VocabularyNLPService:
    """
    Singleton NLP service for vocabulary suggestions.

    This service loads translation models on demand and provides methods to
    generate translations and example sentences for Russian words.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initializes the service with supported language models.
        """
        self._models: Dict[str, str] = {
            'es': 'Helsinki-NLP/opus-mt-ru-es',
            'en': 'Helsinki-NLP/opus-mt-ru-en',
            'pt': 'Helsinki-NLP/opus-mt-ru-pt',
            'fr': 'Helsinki-NLP/opus-mt-ru-fr',
        }
        self._pipelines: Dict[str, Pipeline] = {}

    def _get_translation_pipeline(self, target_language: str) -> Pipeline:
        """
        Returns a translation pipeline for the given target language.
        Loads the model if not already cached.

        Args:
            target_language (str): Target language code (e.g., 'es', 'en').

        Returns:
            Pipeline: A Hugging Face translation pipeline.

        Raises:
            ValueError: If the target language is unsupported.
        """
        if target_language not in self._models:
            raise ValueError(f"Unsupported target language: {target_language}")

        if target_language not in self._pipelines:
            model_name = self._models[target_language]
            logger.info("Loading model for language '%s': %s", target_language, model_name)
            self._pipelines[target_language] = pipeline("translation", model=model_name)

        return self._pipelines[target_language]

    def suggest_translation_and_comment(
        self,
        russian_word: str,
        target_language: str
    ) -> Dict[str, Any]:
        """
        Suggests a translation and a simple example sentence for a given Russian word.

        Args:
            russian_word (str): The word in Russian to be translated.
            target_language (str): The target language code (e.g., 'en', 'es').

        Returns:
            dict: A dictionary with the original word, translated text, and example sentence.
        """
        default_response = {
            "russian_word": russian_word,
            "suggested_translation": f"No translation available for '{target_language}'.",
            "suggested_example_sentence": "Translation service currently unavailable."
        }

        try:
            pipeline_instance = self._get_translation_pipeline(target_language)
            translated = pipeline_instance(russian_word)
            translation = translated[0]["translation_text"]
            return {
                "russian_word": russian_word,
                "suggested_translation": translation,
                "suggested_example_sentence": f"Example: '{translation}'."
            }
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "Translation error for '%s' to '%s': %s",
                russian_word,
                target_language,
                exc,
                exc_info=True
            )
            return default_response


# Global singleton instance
vocabulary_nlp_service = VocabularyNLPService()
