import logging
from typing import Dict, Any, List, Optional

import language_tool_python

logger = logging.getLogger(__name__)

class GrammarService:
    """
    Singleton service for grammar correction using LanguageTool.

    Provides grammar checking and correction for specified languages,
    returning detailed error information and corrected text.
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
        lang_code,
        remote_server="http://languagetool:8010"
        )


    def check_grammar(self, text: str, language: str) -> Dict[str, Any]:
        logger.info("Checking grammar for text in '%s': %.50s...", language, text)

        # Map simplified language codes to LanguageTool locale codes
        lt_language_map = {
            "en": "en-US",
            "es": "es-ES",
            "ru": "ru-RU",
        }
        target_lt_language = lt_language_map.get(language.lower(), language)

        # Initialize or reinitialize LanguageTool if language changed or tool missing
        if self._tool is None or self._current_lt_language != target_lt_language:
            logger.info("LanguageTool (re)initialization for language: %s", target_lt_language)
            try:
                # Clean up previous tool to avoid attribute errors on __del__
                if self._tool:
                    try:
                        self._tool.close()
                    except Exception:
                        pass
                    self._tool = None

                self._tool = self._create_tool(target_lt_language)
                self._current_lt_language = target_lt_language
                logger.info("LanguageTool initialized for %s.", target_lt_language)
            except Exception as e:
                logger.error("Failed to initialize LanguageTool for %s: %s", target_lt_language, e)
                return {
                    "original_text": text,
                    "corrected_text": text,
                    "explanation": f"Failed to load grammar service for '{language}'. Error: {e}",
                    "errors": [],
                    "language": language,
                }

        try:
            matches = self._tool.check(text)
            logger.debug("LanguageTool matches found: %d", len(matches))
        except Exception as e:
            logger.error("Error during LanguageTool check for language '%s': %s", language, e)
            return {
                "original_text": text,
                "corrected_text": text,
                "explanation": f"Error during grammar check for '{language}': {e}. Please try again later.",
                "errors": [],
                "language": language,
            }

        try:
            corrected_text = language_tool_python.utils.correct(text, matches)
        except Exception as e:
            logger.warning("Failed to apply corrections. Returning original text. Error: %s", e)
            corrected_text = text

        explanation_parts: List[str] = []
        errors_list: List[Dict[str, Any]] = []

        for match in matches:
            bad_word = match.context[match.offsetInContext : match.offsetInContext + match.errorLength]
            if match.replacements:
                explanation_parts.append(
                    f"Error: '{match.message}' for '{bad_word}' -> Suggestion: '{match.replacements[0]}'"
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

        return {
            "original_text": text,
            "corrected_text": corrected_text,
            "explanation": explanation,
            "errors": errors_list,
            "language": language,
        }
