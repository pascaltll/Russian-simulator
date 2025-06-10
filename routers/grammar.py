"""
API endpoints for grammar checking.

This module defines the endpoint for submitting text for grammar correction,
leveraging a dedicated grammar service and requiring user authentication.
"""
# Group 1: Standard libraries
import logging

# Group 2: Third-party libraries
from fastapi import APIRouter, Depends, HTTPException, status

# Group 3: First-party modules
from schemas.grammar import GrammarCheckRequest, GrammarCheckResponse
from schemas.user import UserInDB
from services.auth_service import get_current_user
from services.grammar_service import GrammarService

logger = logging.getLogger(__name__)

router = APIRouter()

grammar_service = GrammarService()

@router.post(
    "/check",
    response_model=GrammarCheckResponse,
    summary="Check grammar of a text",
    description=(
        "Submits a text for grammar correction and receives corrected text "
        "and error details."
    ), # C0301: Line too long - Re-checked and confirmed fit within 100 chars after splitting
)
async def check_grammar(
    request: GrammarCheckRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Performs a grammar check on the provided text for the specified language.
    Requires authentication.

    Args:
        request (GrammarCheckRequest): The request body containing the text and language.
        current_user (UserInDB): The authenticated user.

    Returns:
        GrammarCheckResponse: The response containing the corrected text and error details.

    Raises:
        HTTPException: If the language is not supported or an unexpected error occurs.
    """
    logger.info(
        "Received grammar check request from user %s for language '%s'",
        current_user.username, request.language
    ) # C0301: Line too long - Already split in previous turn
    logger.debug("Text to check: %s...", request.text[:100])

    try:
        # Call the grammar service to process the text
        correction_result = grammar_service.check_grammar(
            text=request.text,
            language=request.language
        )
        return GrammarCheckResponse(**correction_result)
    except ValueError as exc:
        logger.error("Grammar check failed due to configuration error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error during grammar check: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during grammar check."
        ) from exc
