from pydantic import BaseModel, Field, ConfigDict # <-- ¡Importa ConfigDict!
from typing import Optional
from datetime import datetime

class AudioSubmissionCreate(BaseModel):
    audio_path: str
    original_transcript: str
    language: Optional[str] = None 

    # ¡Cambio aquí! Reemplaza class Config
    model_config = ConfigDict(from_attributes=True)

class AudioSubmissionResponse(BaseModel):
    id: int
    user_id: int
    audio_path: str
    original_transcript: str
    created_at: Optional[datetime] = None
    language: Optional[str] = None 
    
    # ¡Cambio aquí! Reemplaza class Config
    model_config = ConfigDict(from_attributes=True)