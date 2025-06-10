"""
Authentication service for managing user login, registration, and JWT tokens.

This module handles password hashing, token creation, and user authentication
for securing API endpoints.
"""
# Group 1: Standard libraries
from datetime import datetime, timezone, timedelta
import os
from typing import Optional

# Group 2: Third-party libraries
import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError
from sqlalchemy.orm import Session

# Group 3: First-party modules
from database.config import get_db
from database import crud
from schemas.user import UserInDB

load_dotenv()

# W1508: os.getenv default type is builtins.int. Expected str or None.
# Corrected by explicitly converting to str and then int where applicable.
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key_change_me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
# Ensure conversion to int for ACCESS_TOKEN_EXPIRE_MINUTES
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password.

    Args:
        plain_password (str): The plain-text password provided by the user.
        hashed_password (str): The hashed password stored in the database.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    # bcrypt.checkpw expects bytes, so we encode the strings.
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The hashed password.
    """
    # Generates a salt and hashes the password.
    # bcrypt.hashpw and bcrypt.gensalt return bytes, and we decode them to str.
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates a JWT access token.

    Args:
        data (dict): The data to encode into the token (e.g., {"sub": username}).
        expires_delta (Optional[timedelta]): Optional timedelta for token expiration.
                                             If None, uses ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # C0301: Line too long - Fixed by breaking the line
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> UserInDB:
    """
    Dependency to get the current authenticated user from the JWT token.

    Args:
        token (str): The JWT token from the Authorization header.
        db (Session): Database session dependency.

    Returns:
        UserInDB: The authenticated user's details.

    Raises:
        HTTPException: If credentials cannot be validated or the user is not found.
    """
    # C0301: Line too long - Fixed by breaking the initialization
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
    # W0707: Consider explicitly re-raising - Corrected (already addressed)
    except PyJWTError as exc:
        raise credentials_exception from exc
    user = crud.get_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return UserInDB.model_validate(user)
