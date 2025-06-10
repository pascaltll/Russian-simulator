def _initialize(self):
    """Inicializa el servicio sin instanciar LanguageTool todavía."""
    logger.info("Initializing GrammarService placeholder for LanguageTool...")
    self._tool = None
    self._current_lt_language = None
    logger.info("GrammarService initialized.")

...

try:
    self._tool = language_tool_python.LanguageTool(target_lt_language)
    self._current_lt_language = target_lt_language
    logger.info("LanguageTool successfully initialized for %s.", target_lt_language)
except Exception as e:
    logger.error(
        "Failed to initialize LanguageTool for language %s. Error: %s",
        target_lt_language, e
    )
    return {
        "original_text": text,
        "corrected_text": text,
        "explanation": f"Failed to load grammar service for '{language}'. Please check server logs. Error: {e}",
        "errors": [],
        "language": language
    }

...

except Exception as e:  # noqa: W0718
    logger.warning(
        f"Failed to apply corrections to text. Original text will be returned. Error: {e}"
    )
    corrected_text = text

...

if match.replacements:
    explanation_parts.append(
        f"Error: '{match.message}' for '{bad_word}' -> Suggestion: '{match.replacements[0]}'"
    )
else:
    explanation_parts.append(
        f"Error: '{match.message}' in '{match.context}'"
    )
