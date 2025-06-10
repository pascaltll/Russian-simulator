"""
Pydantic schemas for Audio Submissions.

This module defines the data structures for creating, updating, and responding
with audio submission information, including transcription details.
"""
# Group 1: Standard libraries
from datetime import datetime # Corrected import order (C0411)
from typing import Optional # Corrected import order (C0411)

# Group 2: Third-party libraries
from pydantic import BaseModel, ConfigDict # Removed unused 'Field' import (W0611)

class AudioSubmissionCreate(BaseModel):
    """
    Schema for creating a new audio submission.

    Attributes:
        audio_path (str): The file path where the audio is stored.
        original_transcript (str): The transcribed text from the audio.
        language (Optional[str]): The detected language of the audio/transcript.
    """
    audio_path: str
    original_transcript: str
    language: Optional[str] = None # No trailing whitespace here (C0303)

    # Pydantic v2+ configuration for ORM mode
    model_config = ConfigDict(from_attributes=True)


class AudioSubmissionResponse(BaseModel):
    """
    Schema for responding with audio submission details.

    Attributes:
        id (int): The unique identifier of the audio submission.
        user_id (int): The ID of the user who made the submission.
        audio_path (str): The file path where the audio is stored.
        original_transcript (str): The transcribed text from the audio.
        created_at (Optional[datetime]): Timestamp when the submission was created.
        language (Optional[str]): The detected language of the audio/transcript.
    """
    id: int
    user_id: int
    audio_path: str
    original_transcript: str
    created_at: Optional[datetime] = None
    language: Optional[str] = None # No trailing whitespace here (C0303)

    # Pydantic v2+ configuration for ORM mode
    model_config = ConfigDict(from_attributes=True)
