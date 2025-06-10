"""
SQLAlchemy model for Audio Submissions.

This module defines the database schema for storing audio transcription
requests and their results, linked to a specific user.
"""
# Group 1: Standard libraries
# None for now, as types like Optional are handled by typing.
# Group 2: Third-party libraries
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Corrected import order (C0411)

# Group 3: First-party modules
from database.base_class import Base

# pylint: disable=R0903 # Too few public methods (common for SQLAlchemy models)
class AudioSubmission(Base):
    """
    Represents an audio submission record in the database.

    Attributes:
        id (int): Primary key for the audio submission.
        user_id (int): Foreign key linking to the User who made the submission.
        audio_path (str): The file path where the audio is stored.
        original_transcript (str): The transcribed text from the audio.
        language (str): The detected language of the audio/transcript.
        created_at (datetime): Timestamp when the submission was created.
        owner (User): Relationship to the User model.
    """
    __tablename__ = "audio_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    audio_path = Column(String)
    original_transcript = Column(String)
    language = Column(String, nullable=True)
    # E1102: func.now is not callable (not-callable) - This is a common Pylint false positive
    # with SQLAlchemy's func.now() in server_default. The usage here is typically correct.
    created_at = Column(DateTime(timezone=True), server_default=func.now()) # pylint: disable=E1102

    owner = relationship("User", back_populates="audio_submissions")
