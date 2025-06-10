"""
API endpoints for managing vocabulary items.

This module provides functionalities for suggesting translations and example sentences,
creating, retrieving, and deleting vocabulary items for authenticated users.
"""
# Group 1: Standard libraries
import logging
from typing import List

# Group 2: Third-party libraries
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Group 3: First-party modules
from schemas.vocabulary_item import (
    VocabularyItemCreate,
    VocabularyItemResponse,
    VocabularySuggestionRequest,
    VocabularySuggestionResponse
)
from schemas.user import UserInDB
from services.auth_service import get_current_user
from services.vocabulary_nlp_service import VocabularyNLPService
from database import crud
from database.config import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

nlp_service = VocabularyNLPService()

@router.post(
    "/suggest-translation",
    response_model=VocabularySuggestionResponse,
    summary="Suggest translation and example for a Russian word",
    description=( # C0301 (Line too long - already split)
        "Uses an NLP model to suggest a translation and a simple example sentence "
        "for a given Russian word."
    ),
)
async def suggest_translation(
    request: VocabularySuggestionRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Suggests a translation and an example sentence/comment for a Russian word.

    Args:
        request (VocabularySuggestionRequest):
          The request body containing the Russian word and target language.
        current_user (UserInDB): The authenticated user.

    Returns:
        VocabularySuggestionResponse: The suggested translation and example.
    """
    logger.info(
        "User %s requesting suggestion for '%s'", current_user.username, request.russian_word
        )

    suggestion = nlp_service.suggest_translation_and_comment(
        russian_word=request.russian_word,
        target_language=request.target_language
    )

    return suggestion

@router.post(
    "/",
    response_model=VocabularyItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vocabulary item",
    description=( # C0301 (Line too long - already split)
        "Adds a new Russian word with its translation and an optional example sentence "
        "to the user's vocabulary list."
    ),
)
async def create_vocabulary_item(
    item: VocabularyItemCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new vocabulary item for the authenticated user.

    Args:
        item (VocabularyItemCreate): The data for the new vocabulary item.
        db (Session): Database session dependency.
        current_user (UserInDB): Authenticated user dependency.

    Returns:
        VocabularyItemResponse: The newly created vocabulary item details.
    """
    return crud.create_vocabulary_item(db=db, item=item, user_id=current_user.id)

@router.get(
    "/",
    response_model=List[VocabularyItemResponse],
    summary="Get all vocabulary items for the current user",
    description="Retrieves all vocabulary items associated with the authenticated user.",
)
async def get_user_vocabulary_items(
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Retrieve all vocabulary items belonging to the current user.

    Args:
        db (Session): Database session dependency.
        current_user (UserInDB): Authenticated user dependency.

    Returns:
        list[VocabularyItemResponse]: A list of vocabulary items for the user.
    """
    return crud.get_vocabulary_items_by_user(db=db, user_id=current_user.id)

@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a vocabulary item",
    description=( # C0301 (Line too long - already split)
        "Deletes a specific vocabulary item by its ID, ensuring it belongs "
        "to the authenticated user."
    ),
)
async def delete_vocabulary_item_by_id(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a vocabulary item by its ID.

    Args:
        item_id (int): The ID of the vocabulary item to delete.
        db (Session): Database session dependency.
        current_user (UserInDB): Authenticated user dependency.

    Raises:
        HTTPException: If the vocabulary item is not found or the user
                       does not have permission to delete it.
    """
    deleted = crud.delete_vocabulary_item(db=db, item_id=item_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary item not found or you don't have permission to delete it"
        )
    return {"message": "Vocabulary item deleted successfully"}
