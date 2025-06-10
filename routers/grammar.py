# routers/grammar.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from schemas.grammar import GrammarCheckRequest, GrammarCheckResponse
from schemas.user import UserInDB # Assuming you want to restrict grammar check to authenticated users
from services.auth_service import get_current_user
from services.grammar_service import GrammarService # We will implement this next
from database.config import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

# Instantiate the GrammarService (following the pattern in vocabulary.py)
# If GrammarService had dependencies (like a database session),
# we would use FastAPI's Depends for injection.
grammar_service = GrammarService()

@router.post(
    "/check",
    response_model=GrammarCheckResponse,
    summary="Check grammar of a text",
    description="Submits a text for grammar correction and receives corrected text and error details.",
)
async def check_grammar(
    request: GrammarCheckRequest,
    current_user: UserInDB = Depends(get_current_user) # Ensure only authenticated users can use this
):
    """
    Performs a grammar check on the provided text for the specified language.
    Requires authentication.
    """
    logger.info(f"Received grammar check request from user {current_user.username} for language '{request.language}'")
    logger.debug(f"Text to check: {request.text[:100]}...") # Log first 100 chars

    try:
        # Call the grammar service to process the text
        correction_result = grammar_service.check_grammar(
            text=request.text,
            language=request.language
        )
        return GrammarCheckResponse(**correction_result)
    except ValueError as e:
        logger.error(f"Grammar check failed due to configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during grammar check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during grammar check."
        )