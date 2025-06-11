"""
Service for performing grammar checks on text.

This module provides a singleton GrammarService that integrates with
LanguageTool for actual grammar correction.
"""

import logging
from typing import Dict, Any, List

import language_tool_python

logger = logging.getLogger(__name__)


class GrammarService:
    """
    Singleton service for grammar correction using LanguageTool.

    Provides grammar checking and correction for specified languages,
    returning detailed error information and corrected text.
    """

    _instance: "GrammarService" = None
    _tool: language_tool_python.LanguageTool = None
    _current_lt_language: str = None

    def __new__(cls) -> "GrammarService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initializes the GrammarService placeholder."""
        logger.info("Initializing GrammarService placeholder for LanguageTool...")
        self._tool = None
        self._current_lt_language = None
        logger.info("GrammarService initialized.")

    def check_grammar(self, text: str, language: str) -> Dict[str, Any]:
        """
        Checks and corrects grammar in the given text for the specified language.

        Args:
            text: The input text to check.
            language: Language code (e.g., 'en', 'es', 'ru').

        Returns:
            A dictionary containing the original text, corrected text,
            explanation of corrections, error details, and language code.
        """
        logger.info(
            "Checking grammar for text in '%s': %s...", language, text[:50]
        )

        lt_language_map = {
            "en": "en-US",
            "es": "es-ES",
            "ru": "ru-RU",
        }

        target_lt_language = lt_language_map.get(language.lower(), language)

        if self._tool is None or self._current_lt_language != target_lt_language:
            logger.info(
                "Language mismatch or tool not initialized. Re-initializing LanguageTool for: %s",
                target_lt_language,
            )
            try:
                self._tool = language_tool_python.LanguageTool(target_lt_language)
                self._current_lt_language = target_lt_language
                logger.info("LanguageTool successfully initialized for %s.", target_lt_language)
            except language_tool_python.LanguageToolError as e:
                logger.error(
                    "Failed to initialize LanguageTool for language %s. Error: %s",
                    target_lt_language, e,
                )
                return {
                    "original_text": text,
                    "corrected_text": text,
                    "explanation": (
                        "Failed to load grammar service for '%s'. "
                        "Please check server logs. Error: %s"
                        % (language, e)
                    ),
                    "errors": [],
                    "language": language,
                }

        try:
            matches = self._tool.check(text)
            logger.debug("LanguageTool matches found: %d", len(matches))
        except language_tool_python.LanguageToolError as e:
            logger.error(
                "Error during LanguageTool check for language '%s': %s", language, e
            )
            return {
                "original_text": text,
                "corrected_text": text,
                "explanation": (
                    "Error during grammar check for '%s': %s. Please try again later."
                    % (language, e)
                ),
                "errors": [],
                "language": language,
            }

        try:
            corrected_text = language_tool_python.utils.correct(text, matches)
        except Exception as e:
            logger.warning(
                "Failed to apply corrections to text. Original text will be returned. Error: %s",
                e,
            )
            corrected_text = text

        explanation_parts: List[str] = []
        errors_list: List[Dict[str, Any]] = []

        for match in matches:
            bad_word = match.context[
                match.offsetInContext : match.offsetInContext + match.errorLength
            ]
            if match.replacements:
                explanation_parts.append(
                    "Error: '%s' for '%s' -> Suggestion: '%s'"
                    % (match.message, bad_word, match.replacements[0])
                )
            else:
                explanation_parts.append("Error: '%s' in '%s'" % (match.message, match.context))

            errors_list.append(
                {
                    "message": match.message,
                    "bad_word": bad_word,
                    "suggestions": match.replacements,
                    "offset": match.offset,
                    "length": match.errorLength,
                }
            )

        if not errors_list and text == corrected_text:
            explanation = "No grammar errors found."
        elif errors_list:
            explanation = "Corrections applied:\n" + "\n".join(explanation_parts[:5])
            if len(explanation_parts) > 5:
                explanation += "\n(and more errors...)"
        else:
            explanation = "Corrections made, but no specific explanations generated."

        return {
            "original_text": text,
            "corrected_text": corrected_text,
            "explanation": explanation,
            "errors": errors_list,
            "language": language,
        }
