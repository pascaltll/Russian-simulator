from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Query # Importar Query
from sqlalchemy.orm import Session
from typing import Optional, List # Importar List
import os
import uuid
from pathlib import Path

from database.config import get_db
from database import crud
from schemas.user import UserInDB
from schemas.audio_submission import AudioSubmissionCreate, AudioSubmissionResponse 
from services.auth_service import get_current_user
from utils.whisper_transcriber import transcribe_audio_with_whisper

router = APIRouter()
TEMP_AUDIO_DIR = "temp_audio"
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

@router.post("/transcribe-audio", response_model=AudioSubmissionResponse, status_code=status.HTTP_201_CREATED)
async def transcribe_recorded_audio_endpoint(
    audio_file: UploadFile = File(...),
    language: Optional[str] = None, 
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    allowed_audio_types = ["audio/wav", "audio/mpeg", "audio/mp4", "audio/ogg", "audio/flac", "audio/webm"]
    if audio_file.content_type not in allowed_audio_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Please upload an audio file (e.g., WAV, MP3). Received: {audio_file.content_type}"
        )

    file_extension = Path(audio_file.filename).suffix if audio_file.filename else ".webm"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    temp_file_path = os.path.join(TEMP_AUDIO_DIR, unique_filename)

    try:
        with open(temp_file_path, "wb") as f:
            f.write(await audio_file.read())

        transcription_result = transcribe_audio_with_whisper(temp_file_path)
        transcribed_text = transcription_result.get("text", "Transcription not available.")
        detected_language = transcription_result.get("language", "unknown")

        if "Error" in transcribed_text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transcription failed: {transcribed_text}"
            )

        audio_submission_create = AudioSubmissionCreate(
            audio_path=temp_file_path,
            original_transcript=transcribed_text,
            language=detected_language
        )
        db_submission = crud.create_audio_submission(db=db, submission=audio_submission_create, user_id=current_user.id)
        
        response_data = AudioSubmissionResponse.model_validate(db_submission)

        return response_data

    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing audio: {e}"
        )
    finally:
        # Clean up the temporary file (optional, but good practice)
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@router.post("/upload-and-transcribe", response_model=AudioSubmissionResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_transcribe_audio_endpoint(
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    allowed_audio_types = ["audio/wav", "audio/mpeg", "audio/mp4", "audio/ogg", "audio/flac", "audio/webm"]
    if audio_file.content_type not in allowed_audio_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Please upload an audio file (e.g., WAV, MP3). Received: {audio_file.content_type}"
        )

    file_extension = Path(audio_file.filename).suffix if audio_file.filename else ".webm"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    temp_file_path = os.path.join(TEMP_AUDIO_DIR, unique_filename)

    try:
        with open(temp_file_path, "wb") as f:
            f.write(await audio_file.read())

        transcription_result = transcribe_audio_with_whisper(temp_file_path)
        transcribed_text = transcription_result.get("text", "Transcription not available.")
        detected_language = transcription_result.get("language", "unknown")

        if "Error" in transcribed_text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transcription failed: {transcribed_text}"
            )

        audio_submission_create = AudioSubmissionCreate(
            audio_path=temp_file_path,
            original_transcript=transcribed_text,
            language=detected_language
        )
        db_submission = crud.create_audio_submission(db=db, submission=audio_submission_create, user_id=current_user.id)
        
        response_data = AudioSubmissionResponse.model_validate(db_submission)
        return response_data

    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing audio: {e}"
        )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.get("/my-transcriptions", response_model=list[AudioSubmissionResponse])
def get_user_transcriptions(
    db: Session = Depends(get_db), 
    current_user: UserInDB = Depends(get_current_user),
    # MODIFICACIÓN CLAVE AQUÍ: permitir limit y offset
    offset: int = Query(0, ge=0),
    limit: Optional[int] = Query(5, ge=0, description="Number of items to return. Set to 0 or None for all items.") # Opcional, por defecto 5
):
    # Si limit es 0, interpretamos como "todos"
    if limit == 0:
        limit_val = None
    else:
        limit_val = limit

    submissions = crud.get_audio_submissions_by_user(db, user_id=current_user.id, offset=offset, limit=limit_val)
    return [AudioSubmissionResponse.model_validate(s) for s in submissions]

@router.delete("/transcriptions/{transcription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transcription(
    transcription_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    transcription = db.query(crud.AudioSubmission).filter(
        crud.AudioSubmission.id == transcription_id,
        crud.AudioSubmission.user_id == current_user.id
    ).first()
    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcription not found or you do not have permission to delete it."
        )
    # Eliminar el archivo de audio físico si existe
    if transcription.audio_path and os.path.exists(transcription.audio_path):
        try:
            os.remove(transcription.audio_path)
        except OSError as e:
            # Log the error but don't prevent DB deletion if file can't be removed
            print(f"Error deleting audio file {transcription.audio_path}: {e}")

    # Eliminar la entrada de la base de datos
    if not crud.delete_audio_submission(db, audio_id=transcription_id, user_id=current_user.id):
        # Esta línea es un fallback, crud.delete_audio_submission ya maneja si no se encuentra
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete transcription from database."
        )
    return {"message": "Transcription deleted successfully"}