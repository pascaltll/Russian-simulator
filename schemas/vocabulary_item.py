"""
Pydantic schemas for Vocabulary Items.

This module defines the data structures for creating, retrieving,
and suggesting vocabulary items, including words, translations,
and example sentences.
"""
# Group 1: Standard libraries
from typing import Optional # Corrected import order (C0411)

# Group 2: Third-party libraries
from pydantic import BaseModel, ConfigDict # Corrected import order (C0411)

class VocabularyItemBase(BaseModel):
    """
    Base schema for a vocabulary item, containing core attributes.

    Attributes:
        russian_word (str): The Russian word.
        translation (str): The translation of the Russian word.
        example_sentence (Optional[str]): An optional example sentence using the word.
    """
    russian_word: str
    translation: str
    example_sentence: Optional[str] = None

    # Pydantic v2+ configuration for ORM mode.
    # Added here as a base class might be used with ORM data.
    model_config = ConfigDict(from_attributes=True)


class VocabularyItemCreate(VocabularyItemBase):
    """
    Schema for creating a new vocabulary item.
    Inherits all fields from VocabularyItemBase.
    """
    # No need for pass here, class inherits directly


class VocabularyItemResponse(VocabularyItemBase):
    """
    Schema for responding with vocabulary item details.

    Attributes:
        id (int): The unique identifier of the vocabulary item.
        user_id (Optional[int]): The ID of the user who owns this item.
    """
    id: int
    user_id: Optional[int] = None

    # Pydantic v2+ configuration for ORM mode.
    model_config = ConfigDict(from_attributes=True)


# NEW SCHEMA for suggestion request
class VocabularySuggestionRequest(BaseModel):
    """
    Schema for a vocabulary suggestion request.

    Attributes:
        russian_word (str): The Russian word for which to get a suggestion.
        target_language (str): The target language for translation (e.g., 'es', 'en', 'pt').
    """
    russian_word: str
    target_language: str # 'es', 'en', 'pt'


# NEW SCHEMA for suggestion response
class VocabularySuggestionResponse(BaseModel):
    """
    Schema for a vocabulary suggestion response.

    Attributes:
        russian_word (str): The original Russian word.
        suggested_translation (str): The suggested translation.
        suggested_example_sentence (Optional[str]): A suggested example sentence, if available.
    """
    russian_word: str
    suggested_translation: str
    suggested_example_sentence: Optional[str] = None
