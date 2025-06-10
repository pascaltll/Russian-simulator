"""
Service for performing grammar checks on text.

This module provides a singleton GrammarService that integrates with
LanguageTool for actual grammar correction.
"""
# Group 1: Standard libraries
import logging
from typing import Dict, Any, List

# Group 2: Third-party libraries
import language_tool_python # Importar LanguageTool

logger = logging.getLogger(__name__)

class GrammarService:
    """
    Implements a singleton grammar correction service using LanguageTool.

    This service provides methods to check and correct grammar in a given text
    for specified languages, and provides detailed error information.
    """
    _instance = None
    _tool = None # Atributo para la instancia de LanguageTool
    _current_lt_language = None # Nuevo atributo para rastrear el idioma actual del tool

    def __new__(cls):
        """
        Singleton pattern to ensure only one instance of GrammarService exists.
        """
        if cls._instance is None:
            cls._instance = super(GrammarService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initializes the GrammarService. We will lazily initialize the LanguageTool
        instance in check_grammar based on the requested language.
        """
        logger.info("Initializing GrammarService placeholder for LanguageTool...")
        self._tool = None # Aseguramos que sea None inicialmente
        self._current_lt_language = None # Ningún idioma cargado inicialmente
        logger.info("GrammarService initialized.")


    def check_grammar(self, text: str, language: str) -> Dict[str, Any]:
        """
        Performs grammar correction on the given text using LanguageTool.

        Args:
            text (str): The input text to check.
            language (str): The language of the text (e.g., 'en', 'es', 'ru').
                            LanguageTool expects specific codes like 'en-US', 'es-ES', 'ru-RU'.
                            We'll map common short codes to LanguageTool's expected format.

        Returns:
            Dict[str, Any]: A dictionary conforming to GrammarCheckResponse schema
                            containing the original text, corrected text,
                            an explanation, and a list of errors.
        """
        logger.info("Checking grammar for text in '%s': %s...", language, text[:50])

        # Mapeo de códigos de idioma cortos a los esperados por LanguageTool.
        lt_language_map = {
            "en": "en-US", # English (United States)
            "es": "es-ES", # Spanish (Spain)
            "ru": "ru-RU", # Russian (Russia)
            # Puedes añadir más idiomas aquí si los necesitas:
            # "de": "de-DE", # German
            # "fr": "fr-FR", # French
            # "pt": "pt-PT", # Portuguese (Portugal)
            # "pt-br": "pt-BR" # Portuguese (Brazil)
        }
        
        target_lt_language = lt_language_map.get(language.lower(), language)
        
        # Lógica clave: Reinicializar LanguageTool si el idioma solicitado es diferente
        # del idioma de la instancia actualmente cargada.
        if self._tool is None or self._current_lt_language != target_lt_language:
            logger.info(f"Language mismatch or tool not initialized. Re-initializing LanguageTool for: {target_lt_language}")
            try:
                # Aquí se crea una nueva instancia de LanguageTool con el idioma correcto.
                # Nota: La primera vez que se carga un idioma, puede haber una ligera demora
                # mientras LanguageTool descarga los datos necesarios.
                self._tool = language_tool_python.LanguageTool(target_lt_language)
                self._current_lt_language = target_lt_language
                logger.info(f"LanguageTool successfully initialized for {target_lt_language}.")
            except Exception as e:
                logger.error(f"Failed to initialize LanguageTool for language {target_lt_language}. Error: %s", e)
                # Si falla la inicialización para el idioma solicitado, devolvemos un error.
                return {
                    "original_text": text,
                    "corrected_text": text,
                    "explanation": f"Failed to load grammar service for '{language}'. Please check server logs. Error: {e}",
                    "errors": [],
                    "language": language
                }

        # Ahora que sabemos que _tool está inicializado con el idioma correcto,
        # podemos proceder con la comprobación.
        try:
            # Realiza la comprobación gramatical. No se pasa el argumento 'language' aquí.
            matches = self._tool.check(text) 
            logger.debug("LanguageTool matches found: %s", len(matches))
        except Exception as e:
            logger.error("Error during LanguageTool check for language '%s': %s", language, e)
            return {
                "original_text": text,
                "corrected_text": text,
                "explanation": f"Error during grammar check for '{language}': {e}. Please try again later.",
                "errors": [],
                "language": language
            }

        corrected_text = text
        explanation_parts = []
        errors_list: List[Dict[str, Any]] = []

        try:
            corrected_text = language_tool_python.utils.correct(text, matches)
        except Exception as e:
            logger.warning(f"Failed to apply corrections to text. Original text will be returned. Error: {e}")
            corrected_text = text

        for match in matches:
            if match.replacements:
                explanation_parts.append(f"Error: '{match.message}' for '{match.context[match.offsetInContext : match.offsetInContext + match.errorLength]}' -> Suggestion: '{match.replacements[0]}'")
            else:
                explanation_parts.append(f"Error: '{match.message}' in '{match.context}'")

            errors_list.append({
                "message": match.message,
                "bad_word": match.context[match.offsetInContext : match.offsetInContext + match.errorLength], 
                "suggestions": match.replacements,
                "offset": match.offset,
                "length": match.errorLength
            })

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
            "language": language
        }