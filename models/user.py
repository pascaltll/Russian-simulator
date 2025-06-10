"""
SQLAlchemy model for Users.

This module defines the database schema for storing user information,
including authentication details and links to their audio submissions
and vocabulary items.
"""
# Group 1: Standard libraries
# None for now.

# Group 2: Third-party libraries
from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Ensure func is imported from sqlalchemy.sql

# Group 3: First-party modules
from database.base_class import Base

# pylint: disable=R0903 # Too few public methods (common for SQLAlchemy models)
class User(Base):
    """
    Represents a user record in the database.

    Attributes:
        id (int): Primary key for the user.
        telegram_id (int, optional): Unique ID for Telegram users.
        username (str, optional): Unique username.
        email (str, optional): Unique email address.
        hashed_password (str, optional): Hashed password for authentication.
        first_name (str, optional): User's first name.
        last_name (str, optional): User's last name.
        created_at (datetime): Timestamp when the user was created.
        updated_at (datetime): Timestamp of the last update to the user record.
        audio_submissions (list): Relationship to AudioSubmission models.
        vocabulary_items (list): Relationship to VocabularyItem models.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    # E1102: func.now is not callable (not-callable) - This is a common Pylint false positive
    # with SQLAlchemy's func.now() in server_default/onupdate. The usage here is typically correct.
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # pylint: disable=E1102
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) # pylint: disable=E1102

    audio_submissions = relationship("AudioSubmission", back_populates="owner")
    vocabulary_items = relationship("VocabularyItem", back_populates="owner")
