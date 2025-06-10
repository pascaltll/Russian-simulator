"""
Pydantic schemas for Grammar Checking.

This module defines the data structures for grammar check requests and responses,
including details about individual grammar errors.
"""
# Group 1: Standard libraries
from typing import List, Optional

# Group 2: Third-party libraries
from pydantic import BaseModel, Field

class GrammarCheckRequest(BaseModel):
    """
    Schema for the grammar check request.

    Attributes:
        text (str): The text to be checked for grammar errors.
        language (str): The language of the text (e.g., 'en' for English, 'es' for Spanish).
    """
    text: str = Field(..., description="The text to be checked for grammar errors.")
    language: str = Field( # C0301: Line too long - Split description
        ..., description="The language of the text (e.g., 'en' for English, 'es' for Spanish)."
    )

class GrammarError(BaseModel):
    """
    Represents a single grammar error found in the text.

    Attributes:
        message (str): A human-readable message describing the error.
        bad_word (str): The word or phrase that contains the error.
        suggestions (List[str]): List of possible corrections for the error.
        offset (int): The starting character offset of the error in the original text.
        length (int): The length of the erroneous segment in the original text.
    """
    message: str = Field( # C0301: Line too long - Split description
        ..., description="A human-readable message describing the error."
    )
    bad_word: str = Field( # C0301: Line too long - Split description
        ..., description="The word or phrase that contains the error."
    )
    suggestions: List[str] = Field( # C0301: Line too long - Split description
        default_factory=list,
        description="List of possible corrections for the error."
    )
    offset: int = Field( # C0301: Line too long - Split description
        ..., description="The starting character offset of the error in the original text."
    )
    length: int = Field( # C0301: Line too long - Split description
        ..., description="The length of the erroneous segment in the original text."
    )

class GrammarCheckResponse(BaseModel):
    """
    Schema for the grammar check response.

    Attributes:
        original_text (str): The original text submitted for grammar checking.
        corrected_text (str): The text after grammar correction.
        explanation (Optional[str]): A general explanation of the corrections made.
        errors (List[GrammarError]): A list of detailed grammar errors found.
        language (str): The language of the processed text.
    """
    original_text: str = Field( # C0301: Line too long - Split description
        ..., description="The original text submitted for grammar checking."
    )
    corrected_text: str = Field( # C0301: Line too long - Split description
        ..., description="The text after grammar correction."
    )
    explanation: Optional[str] = Field( # C0301: Line too long - Split description
        None, description="A general explanation of the corrections made."
    )
    errors: List[GrammarError] = Field( # C0301: Line too long - Split description
        default_factory=list,
        description="A list of detailed grammar errors found."
    )
    language: str = Field(..., description="The language of the processed text.")
