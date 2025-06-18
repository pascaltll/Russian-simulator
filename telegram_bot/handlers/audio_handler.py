"""
Handlers for processing audio, voice, and video messages in the Telegram bot.
This module uses Whisper to transcribe audio content and stores results in the database.
"""

import logging
import os
import uuid
from pathlib import Path
from typing import Generator, Optional, Tuple

from telegram import Update, Message
from telegram.ext import ContextTypes
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from sqlalchemy.orm import Session
import sqlalchemy.exc
import telegram.error

from database.config import get_db
from database import crud
from schemas.user import UserCreateTelegram, UserInDB
from schemas.audio_submission import AudioSubmissionCreate
from utils.whisper_transcriber import transcribe_audio_with_whisper

logger = logging.getLogger(__name__)

TEMP_FILES_DIR = "temp_audio"
os.makedirs(TEMP_FILES_DIR, exist_ok=True)


def get_db_session() -> Generator[Session, None, None]:
    """Yield a database session from the configured generator."""
    yield from get_db()


async def save_telegram_file(telegram_file, _user_id: int, extension: str) -> str:
    """Download a Telegram file and save it locally with a unique name."""
    file_name = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(TEMP_FILES_DIR, file_name)
    await telegram_file.download_to_drive(file_path)
    logger.info("Temporary file saved: %s", file_path)
    return file_path


async def _create_or_get_user(
    db: Session, update: Update, user_id: int
) -> UserInDB:
    """Create or retrieve a user from the database."""
    db_user = crud.get_user_by_telegram_id(db, user_id)
    if not db_user:
        user_data = UserCreateTelegram(
            telegram_id=user_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name,
            email=None,
            hashed_password=None,
        )
        try:
            db_user = crud.create_telegram_user(db, user_data)
        except sqlalchemy.exc.SQLAlchemyError as db_exc:
            logger.error("DB error creating user: %s", db_exc, exc_info=True)
            raise
    return db_user


async def _transcribe_and_save(
    db: Session, file_path: str, user_id: int
) -> Tuple[str, str]:
    """Transcribe audio and save submission to the database."""
    try:
        transcription_result = transcribe_audio_with_whisper(file_path)
        transcription_text = transcription_result.get("text")
        detected_language = transcription_result.get("language")

        if transcription_text and (
            transcription_text.startswith("Error") or
            transcription_text.startswith("Whisper transcription error")
        ):
            raise ValueError(transcription_text)

        crud.create_audio_submission(
            db,
            submission=AudioSubmissionCreate(
                audio_path=file_path,
                original_transcript=transcription_text,
                language=detected_language,
            ),
            user_id=user_id,
        )
        return transcription_text, detected_language
    except (ValueError, CouldntDecodeError, sqlalchemy.exc.SQLAlchemyError) as exc:
        logger.error("Error in transcription or DB save: %s", exc, exc_info=True)
        raise


async def _handle_error(
    update: Update,
    progress_message: Optional[Message],
    user_id: int,
    exc: Exception,
    message: str = "An error occurred while processing your message",
) -> None:
    """Handle errors and send error messages."""
    logger.error("Error for user %s: %s", user_id, exc, exc_info=True)
    if progress_message:
        try:
            await progress_message.delete()
        except telegram.error.TelegramError as delete_exc:
            logger.warning(
                "Could not delete error-related progress message %s: %s",
                progress_message.message_id,
                delete_exc,
            )
    await update.message.reply_text(f"{message}: {str(exc)[:100]}")


async def _process_audio_transcription(
    update: Update,
    file_path: str,
    user_id: int,
    progress_message: Optional[Message] = None,
):
    """Transcribe an audio file and store the result in the database."""
    db = next(get_db_session())
    if progress_message is None:
        await update.message.chat.send_action("typing")
        progress_message = await update.message.reply_text("Processing your audio...")

    try:
        db_user = await _create_or_get_user(db, update, user_id)
        transcription_text, detected_language = await _transcribe_and_save(
            db,
            file_path,
            db_user.id,
        )

        try:
            await progress_message.delete()
            logger.info("Deleted progress message: %s", progress_message.message_id)
        except telegram.error.TelegramError as exc:
            logger.warning(
                "Could not delete progress message %s: %s",
                progress_message.message_id,
                exc,
            )

        output_message = (
            "Transcription Result\n"
            f"Language: {detected_language.upper()}\n\n"
            f"`{transcription_text}`"
        )
        await update.message.reply_text(output_message, parse_mode="Markdown")

    except (ValueError, sqlalchemy.exc.SQLAlchemyError, telegram.error.TelegramError) as exc:
        await _handle_error(update, progress_message, user_id, exc)
    except (RuntimeError, TypeError) as exc:
        await _handle_error(
            update,
            progress_message,
            user_id,
            exc,
            "An unexpected error occurred while processing your message",
        )
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info("Temporary file deleted: %s", file_path)
            except OSError as exc:
                logger.error("Error deleting temporary file %s: %s", file_path, exc)


async def handle_audio(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming audio messages and trigger transcription."""
    user_id = update.effective_user.id
    audio_file = await update.message.audio.get_file()
    file_extension = Path(audio_file.file_path).suffix if audio_file.file_path else '.mp3'
    file_path = await save_telegram_file(audio_file, user_id, file_extension)
    await _process_audio_transcription(update, file_path, user_id)


async def handle_voice(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming voice messages and trigger transcription."""
    user_id = update.effective_user.id
    voice_file = await update.message.voice.get_file()
    file_extension = ".ogg"
    file_path = await save_telegram_file(voice_file, user_id, file_extension)
    await _process_audio_transcription(update, file_path, user_id)


async def _extract_audio_from_video(
    video_file, user_id: int, video_extension: str
) -> Tuple[str, str]:
    """Extract audio from a video file."""
    video_path = await save_telegram_file(video_file, user_id, video_extension)
    try:
        video_segment = AudioSegment.from_file(video_path)
        audio_path = os.path.join(TEMP_FILES_DIR, f"{uuid.uuid4()}.mp3")
        video_segment.export(audio_path, format="mp3")
        logger.info("Audio extracted to: %s", audio_path)
        return audio_path, video_path
    except (CouldntDecodeError, OSError, ValueError) as exc:
        logger.error("Error extracting audio from video: %s", exc, exc_info=True)
        raise


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming video or video notes, extract audio, and transcribe."""
    user_id = update.effective_user.id
    message = update.message
    video_file = None
    video_extension = ".mp4"
    progress_message = None
    video_path = None

    try:
        if message.video_note:
            video_file = await message.video_note.get_file()
            await context.bot.send_chat_action(chat_id=user_id, action="record_video")
            progress_message = await context.bot.send_message(user_id, "Processing your video...")
        elif message.video:
            video_file = await message.video.get_file()
            if message.video.mime_type and '/' in message.video.mime_type:
                video_extension = f".{message.video.mime_type.split('/')[-1]}"
            await context.bot.send_chat_action(chat_id=user_id, action="upload_video")
            progress_message = await context.bot.send_message(user_id, "Processing your video...")
        else:
            await context.bot.send_message(user_id, "Unrecognized video type.")
            return

        audio_path, video_path = await _extract_audio_from_video(
            video_file, user_id,
            video_extension
            )
        await _process_audio_transcription(update, audio_path, user_id, progress_message)

    except (telegram.error.TelegramError, OSError, ValueError) as exc:
        await _handle_error(update, progress_message, user_id, exc,
                            "An error occurred while processing your video")
    except (RuntimeError, TypeError) as exc:
        await _handle_error(
            update,
            progress_message,
            user_id,
            exc,
            "An unexpected error occurred while processing your video",
        )
    finally:
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
                logger.info("Temporary video file deleted: %s", video_path)
            except OSError as exc:
                logger.error("Error deleting temporary video file %s: %s", video_path, exc)
