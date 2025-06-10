from pydantic import BaseModel, ConfigDict # <-- ¡Importa ConfigDict!
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

    model_config = ConfigDict(from_attributes=True) # <-- ¡Cambio aquí! Reemplaza class Config

# NUEVO ESQUEMA para la solicitud de sugerencia
class VocabularySuggestionRequest(BaseModel):
    russian_word: str
    target_language: str # 'es', 'en', 'pt'

# NUEVO ESQUEMA para la respuesta de sugerencia
class VocabularySuggestionResponse(BaseModel):
    russian_word: str
    suggested_translation: str
    suggested_example_sentence: Optional[str] = None