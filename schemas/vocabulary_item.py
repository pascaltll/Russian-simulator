# schemas/vocabulary_item.py
from pydantic import BaseModel
from typing import Optional

class VocabularyItemBase(BaseModel):
    russian_word: str
    translation: str
    example_sentence: Optional[str] = None

class VocabularyItemCreate(VocabularyItemBase):
    pass

class VocabularyItemResponse(VocabularyItemBase):
    id: int
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

# NUEVO ESQUEMA para la solicitud de sugerencia
class VocabularySuggestionRequest(BaseModel):
    russian_word: str
    target_language: str # 'es', 'en', 'pt'

# NUEVO ESQUEMA para la respuesta de sugerencia
class VocabularySuggestionResponse(BaseModel):
    russian_word: str
    suggested_translation: str
    suggested_example_sentence: Optional[str] = None