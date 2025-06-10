from pydantic import BaseModel, EmailStr, ConfigDict # <-- ¡Asegúrate de que ConfigDict esté aquí!
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str

class UserCreateTelegram(BaseModel):
    telegram_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    hashed_password: Optional[str] = None

    # ¡CAMBIO CLAVE AQUÍ!
    model_config = ConfigDict(from_attributes=True) # Reemplaza 'class Config:'

class UserInDB(UserBase):
    id: int
    telegram_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # ¡CAMBIO CLAVE AQUÍ!
    model_config = ConfigDict(from_attributes=True) # Reemplaza 'class Config:'

class Token(BaseModel):
    access_token: str
    token_type: str