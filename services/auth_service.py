from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError, jwt # Ya eliminada
import bcrypt
# ¡CORRECCIÓN AQUÍ!
import jwt # Importa la librería PyJWT como 'jwt'
from jwt.exceptions import PyJWTError # Importa la excepción específica
from datetime import datetime, timezone, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

from database.config import get_db
from database import crud
from schemas.user import UserInDB
from sqlalchemy.orm import Session

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key_change_me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError: # Esto se mantiene igual
        raise credentials_exception
    user = crud.get_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return UserInDB.model_validate(user)