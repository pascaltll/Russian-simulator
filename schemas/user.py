"""
Pydantic schemas for User management and authentication.

This module defines the data structures for user creation,
user representation in the database, and authentication tokens.
"""
# Group 1: Standard libraries
from datetime import datetime
from typing import Optional

# Group 2: Third-party libraries
from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    """
    Base schema for a user, containing common attributes.

    Attributes:
        username (str): The user's unique username.
        email (Optional[EmailStr]): The user's email address, optional.
    """
    username: str
    email: Optional[EmailStr] = None

    # Pydantic v2+ configuration for ORM mode.
    # Added here as a base class might be used with ORM data.
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    """
    Schema for creating a new user. Inherits from UserBase and adds a password.

    Attributes:
        password (str): The user's plain text password (will be hashed).
    """
    password: str


class UserCreateTelegram(BaseModel):
    """
    Schema for creating a user specifically from Telegram interaction.

    Attributes:
        telegram_id (int): The unique Telegram user ID.
        first_name (Optional[str]): User's first name from Telegram.
        last_name (Optional[str]): User's last name from Telegram.
        username (Optional[str]): User's Telegram username.
        email (Optional[EmailStr]): User's email address from Telegram.
        hashed_password (Optional[str]): The hashed password, if applicable for Telegram users.
    """
    telegram_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    hashed_password: Optional[str] = None

    # Pydantic v2+ configuration for ORM mode.
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserBase):
    """
    Schema for representing a user as stored in the database.
    Includes database-generated fields and hashed password (not exposed directly).

    Attributes:
        id (int): The unique identifier of the user in the database.
        telegram_id (Optional[int]): The unique Telegram user ID.
        first_name (Optional[str]): User's first name.
        last_name (Optional[str]): User's last name.
        created_at (Optional[datetime]): Timestamp when the user record was created.
        updated_at (Optional[datetime]): Timestamp of the last update to the user record.
    """
    id: int
    telegram_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Pydantic v2+ configuration for ORM mode.
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """
    Schema for the authentication token response.

    Attributes:
        access_token (str): The JWT access token.
        token_type (str): The type of token (e.g., "bearer").
    """
    access_token: str
    token_type: str
