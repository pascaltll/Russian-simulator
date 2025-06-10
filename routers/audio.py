"""
API endpoints for handling audio submissions, including transcription
and management of user transcriptions.
"""
# Group 1: Standard libraries
import os
import uuid
from pathlib import Path
from typing import Optional, List

# Group 2: Third-party libraries
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session

# Group 3: First-party modules
from database.config import get_db
from database import crud
from schemas.user import UserInDB
from schemas.audio_submission import AudioSubmissionCreate, AudioSubmissionResponse
from services.auth_service import get_current_user
from utils.whisper_transcriber import transcribe_audio_with_whisper

router = APIRouter()
TEMP_AUDIO_DIR = "temp_audio"
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

# Helper function to reduce code duplication (addresses R0801 implicitly)
async def _process_audio_for_transcription(
    audio_file: UploadFile,
    db: Session,
    current_user: UserInDB
) -> AudioSubmissionResponse:
    """
    Handles the common logic for processing an uploaded audio file,
    transcribing it, saving the submission to the DB, and cleaning up.
    """
    # C0301: Line too long - Corrected by splitting the list
    allowed_audio_types = [
        "audio/wav", "audio/mpeg", "audio/mp4", "audio/ogg",
        "audio/flac", "audio/webm"
    ]
    if audio_file.content_type not in allowed_audio_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported file type. Please upload an audio file (e.g., WAV, MP3). "
                f"Received: {audio_file.content_type}"
            )
        )

    file_extension = Path(audio_file.filename).suffix if audio_file.filename else ".webm"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    temp_file_path = os.path.join(TEMP_AUDIO_DIR, unique_filename)

    try:
        with open(temp_file_path, "wb") as file_object:
            file_object.write(await audio_file.read())

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
        # C0301: Line too long - Corrected by splitting the function call
        db_submission = crud.create_audio_submission(
            db=db, submission=audio_submission_create, user_id=current_user.id
        )

        response_data = AudioSubmissionResponse.model_validate(db_submission)
        return response_data

    # W0707: Consider explicitly re-raising - Corrected (already addressed in prior versions)
    except Exception as exc:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing audio: {exc}"
        ) from exc
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@router.post(
    "/transcribe-audio",
    response_model=AudioSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Transcribe recorded audio and save as submission"
)
async def transcribe_recorded_audio_endpoint(
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Handles the transcription of a recorded audio file.

    Expects an audio file and an authenticated user.
    Transcribes the audio, saves the submission to the database,
    and returns the transcription details.
    """
    return await _process_audio_for_transcription(audio_file, db, current_user)


@router.post(
    "/upload-and-transcribe",
    response_model=AudioSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload an audio file and transcribe it"
)
async def upload_and_transcribe_audio_endpoint(
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Handles the upload and transcription of an audio file.

    This endpoint is largely similar to /transcribe-audio but
    can be used for direct file uploads.
    """
    return await _process_audio_for_transcription(audio_file, db, current_user)


@router.get(
    "/my-transcriptions",
    response_model=List[AudioSubmissionResponse],
    summary="Get all audio transcriptions for the current user"
)
def get_user_transcriptions(
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
    offset: int = Query(0, ge=0, description="Offset for pagination (skip this many items)"),
    limit: Optional[int] = Query(
        5, ge=0, description="Number of items to return. Set to 0 or None for all items."
    )
):
    """
    Retrieves a paginated list of audio transcriptions belonging to the current user.

    Args:
        db (Session): Database session dependency.
        current_user (UserInDB): Authenticated user dependency.
        offset (int): Number of items to skip (for pagination).
        limit (Optional[int]): Maximum number of items to return.
                                If 0 or None, all items are returned.

    Returns:
        list[AudioSubmissionResponse]: A list of audio submission responses.
    """
    limit_val = None if limit == 0 else limit

    # C0301: Line too long - Corrected by splitting the function call
    submissions = crud.get_audio_submissions_by_user(
        db, user_id=current_user.id, offset=offset, limit=limit_val
    )
    return [AudioSubmissionResponse.model_validate(s) for s in submissions]


@router.delete(
    "/transcriptions/{transcription_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific audio transcription"
)
async def delete_transcription(
    transcription_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Deletes an audio transcription record and its associated audio file.

    Args:
        transcription_id (int): The ID of the transcription to delete.
        db (Session): Database session dependency.
        current_user (UserInDB): Authenticated user dependency.

    Returns:
        dict: A message indicating successful deletion.

    Raises:
        HTTPException: If the transcription is not found or the user
                       does not have permission to delete it.
    """
    # C0301: Line too long - Corrected by splitting the filter chain
    transcription = db.query(crud.AudioSubmission).filter(
        crud.AudioSubmission.id == transcription_id,
        crud.AudioSubmission.user_id == current_user.id
    ).first()

    if not transcription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcription not found or you do not have permission to delete it."
        )

    # Delete the physical audio file if it exists
    if transcription.audio_path and os.path.exists(transcription.audio_path):
        try:
            os.remove(transcription.audio_path)
        except OSError as exc:
            # For a real application, you might use a logger here
            # logging.error("Error deleting audio file %s: %s", transcription.audio_path, exc)
            print(f"Error deleting audio file {transcription.audio_path}: {exc}")

    # Delete the database entry
    if not crud.delete_audio_submission(db, audio_id=transcription_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete transcription from database."
        ) from None
    return {"message": "Transcription deleted successfully"}
