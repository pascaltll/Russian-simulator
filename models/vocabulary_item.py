"""
SQLAlchemy model for Vocabulary Items.

This module defines the database schema for storing vocabulary entries,
including Russian words, their translations, example sentences,
and a link to the user who owns them.
"""
# Group 1: Standard libraries
# None for now.

# Group 2: Third-party libraries
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Group 3: First-party modules
from database.base_class import Base # Ensure Base import is correct

# pylint: disable=R0903 # Too few public methods (common for SQLAlchemy models)
class VocabularyItem(Base):
    """
    Represents a vocabulary item record in the database.

    Attributes:
        id (int): Primary key for the vocabulary item.
        russian_word (str): The Russian word.
        translation (str): The translation of the Russian word.
        example_sentence (str, optional): An example sentence using the word.
        user_id (int): Foreign key linking to the User who owns this item.
        created_at (datetime): Timestamp when the vocabulary item was created.
        owner (User): Relationship to the User model.
    """
    __tablename__ = "vocabulary_items"

    id = Column(Integer, primary_key=True, index=True)
    russian_word = Column(String, index=True)
    translation = Column(String)
    example_sentence = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    # E1102: func.now is not callable (not-callable) - This is a common Pylint false positive
    # with SQLAlchemy's func.now() in server_default. The usage here is typically correct.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True) # pylint: disable=E1102

    owner = relationship("User", back_populates="vocabulary_items")
