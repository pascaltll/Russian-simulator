"""Grammar correction service using LanguageTool.

This module provides a singleton service for checking and correcting grammar in text
using the LanguageTool API. It supports multiple languages and provides detailed
error explanations.
"""

import logging
from typing import Dict, Any, List, Optional

import language_tool_python

logger = logging.getLogger(__name__)


class GrammarService:
    """
    Singleton service for grammar correction using LanguageTool.
    """

    _instance: Optional["GrammarService"] = None
    _tool: Optional[language_tool_python.LanguageTool] = None
    _current_lt_language: Optional[str] = None

    def __new__(cls) -> "GrammarService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        logger.info("GrammarService initialized.")
        self._tool = None
        self._current_lt_language = None

    def _create_tool(self, lang_code: str) -> language_tool_python.LanguageTool:
        return language_tool_python.LanguageTool(
            lang_code, remote_server="http://languagetool:8010"
        )

    def _init_tool_if_needed(self, language: str) -> Optional[str]:
        """
        Initializes or reinitializes the LanguageTool instance if the language has changed.
        Returns an error message if initialization fails, otherwise None.
        """
        lt_language_map = {
            "en": "en-US",
            "es": "es-ES",
            "ru": "ru-RU",
        }
        target_lt_language = lt_language_map.get(language.lower(), language)

        if self._tool is None or self._current_lt_language != target_lt_language:
            logger.info("LanguageTool (re)initialization for language: %s", target_lt_language)
            try:
                if self._tool:
                    try:
                        self._tool.close()
                    except Exception as close_error:  # pylint: disable=broad-except
                        logger.warning("Error closing LanguageTool: %s", close_error)
                    self._tool = None

                self._tool = self._create_tool(target_lt_language)
                self._current_lt_language = target_lt_language
                logger.info("LanguageTool initialized for %s.", target_lt_language)
            except Exception as init_error:  # pylint: disable=broad-except
                logger.error("Failed to initialize LanguageTool for %s: %s",
                           target_lt_language, init_error)
                return f"Failed to load grammar service for '{language}'. Error: {init_error}"
        return None

    def _generate_explanation(self,
                             text: str,
                             corrected_text: str,
                             matches: List[Any]) -> (str, List[Dict[str, Any]]):
        """
        Creates a user-friendly explanation and list of errors from LanguageTool matches.
        """
        explanation_parts: List[str] = []
        errors_list: List[Dict[str, Any]] = []

        for match in matches:
            bad_word = match.context[
                match.offsetInContext: match.offsetInContext + match.errorLength
            ]
            if match.replacements:
                explanation_parts.append(
                    f"Error: '{match.message}' for '{bad_word}' -> Suggestion: '{
                        match.replacements[0]
                        }'"
                )
            else:
                explanation_parts.append(f"Error: '{match.message}' in '{match.context}'")

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

        return explanation, errors_list

    def check_grammar(self, text: str, language: str) -> Dict[str, Any]:
        """
        Checks and corrects grammar in the given text for the specified language.
        """
        logger.info("Checking grammar for text in '%s': %.50s...", language, text)

        error_msg = self._init_tool_if_needed(language)
        if error_msg:
            return {
                "original_text": text,
                "corrected_text": text,
                "explanation": error_msg,
                "errors": [],
                "language": language,
            }

        try:
            matches = self._tool.check(text)
            logger.debug("LanguageTool matches found: %d", len(matches))
        except Exception as check_error:  # pylint: disable=broad-except
            logger.error("Error during grammar check for language '%s': %s", language, check_error)
            return {
                "original_text": text,
                "corrected_text": text,
                "explanation": (
                    f"Error during grammar check for '{language}': {check_error}. "
                    "Please try again later."
                ),
                "errors": [],
                "language": language,
            }

        try:
            corrected_text = language_tool_python.utils.correct(text, matches)
        except Exception as correct_error:  # pylint: disable=broad-except
            logger.warning(
                "Failed to apply corrections. Returning original text. Error: %s", correct_error
                )
            corrected_text = text

        explanation, errors = self._generate_explanation(text, corrected_text, matches)

        return {
            "original_text": text,
            "corrected_text": corrected_text,
            "explanation": explanation,
            "errors": errors,
            "language": language,
        }
