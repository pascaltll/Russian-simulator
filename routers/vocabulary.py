# routers/vocabulary.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

# Importaciones de tus esquemas y servicios necesarios
from schemas.vocabulary_item import (
    VocabularyItemCreate,
    VocabularyItemResponse,
    VocabularySuggestionRequest,
    VocabularySuggestionResponse
)
from schemas.user import UserInDB # Import UserInDB for get_current_user type
from services.auth_service import get_current_user
from services.vocabulary_nlp_service import VocabularyNLPService # Importa la clase del servicio NLP
from database import crud
from database.config import get_db

logger = logging.getLogger(__name__)

# ¡MUY IMPORTANTE! Define tu APIRouter aquí
router = APIRouter()

# Crea una instancia del servicio NLP (se inicializará una vez debido al patrón Singleton)
nlp_service = VocabularyNLPService()

# Endpoint para la sugerencia de traducción y comentario
@router.post(
    "/suggest-translation",
    response_model=VocabularySuggestionResponse,
    summary="Suggest translation and example for a Russian word",
    description="Uses an NLP model to suggest a translation and a simple example sentence for a given Russian word.",
)
async def suggest_translation(
    request: VocabularySuggestionRequest,
    current_user: UserInDB = Depends(get_current_user) # Asegúrate de que UserInDB es el tipo correcto
):
    """
    Sugiere traducción y una frase de ejemplo/comentario para una palabra en ruso.
    """
    logger.info(f"User {current_user.username} requesting suggestion for '{request.russian_word}'")

    # Llama al servicio NLP para obtener la traducción y el comentario
    suggestion = nlp_service.suggest_translation_and_comment(
        russian_word=request.russian_word,
        target_language=request.target_language
    )

    return suggestion # Esto ya devuelve un diccionario con las claves correctas

# Endpoint para crear un elemento de vocabulario
@router.post(
    "/",
    response_model=VocabularyItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vocabulary item",
    description="Adds a new Russian word with its translation and an optional example sentence to the user's vocabulary list.",
)
async def create_vocabulary_item(
    item: VocabularyItemCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a new vocabulary item for the authenticated user.
    """
    return crud.create_vocabulary_item(db=db, item=item, user_id=current_user.id)

# Endpoint para obtener todos los elementos de vocabulario de un usuario
@router.get(
    "/",
    response_model=list[VocabularyItemResponse],
    summary="Get all vocabulary items for the current user",
    description="Retrieves all vocabulary items associated with the authenticated user.",
)
async def get_user_vocabulary_items(
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Retrieve all vocabulary items belonging to the current user.
    """
    return crud.get_vocabulary_items_by_user(db=db, user_id=current_user.id)

# Endpoint para eliminar un elemento de vocabulario
@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a vocabulary item",
    description="Deletes a specific vocabulary item by its ID, ensuring it belongs to the authenticated user.",
)
async def delete_vocabulary_item_by_id(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a vocabulary item by its ID.
    """
    deleted = crud.delete_vocabulary_item(db=db, item_id=item_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary item not found or you don't have permission to delete it"
        )
    return {"message": "Vocabulary item deleted successfully"}