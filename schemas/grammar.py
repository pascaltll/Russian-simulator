# schemas/grammar.py
from pydantic import BaseModel, Field
from typing import List, Optional

class GrammarCheckRequest(BaseModel):
    """
    Schema for the grammar check request.
    """
    text: str = Field(..., description="The text to be checked for grammar errors.")
    language: str = Field(..., description="The language of the text (e.g., 'en' for English, 'es' for Spanish).")

class GrammarError(BaseModel):
    """
    Represents a single grammar error found in the text.
    """
    message: str = Field(..., description="A human-readable message describing the error.")
    bad_word: str = Field(..., description="The word or phrase that contains the error.")
    suggestions: List[str] = Field(default_factory=list, description="List of possible corrections for the error.")
    offset: int = Field(..., description="The starting character offset of the error in the original text.")
    length: int = Field(..., description="The length of the erroneous segment in the original text.")

class GrammarCheckResponse(BaseModel):
    """
    Schema for the grammar check response.
    """
    original_text: str = Field(..., description="The original text submitted for grammar checking.")
    corrected_text: str = Field(..., description="The text after grammar correction.")
    explanation: Optional[str] = Field(None, description="A general explanation of the corrections made.")
    errors: List[GrammarError] = Field(default_factory=list, description="A list of detailed grammar errors found.")
    language: str = Field(..., description="The language of the processed text.")