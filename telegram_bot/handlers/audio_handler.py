import logging
import os
from telegram import Update, Message
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from typing import Generator, Optional
import uuid
from pathlib import Path

from pydub import AudioSegment

from database.config import get_db
from database import crud
from models.user import User
from schemas.user import UserCreateTelegram
from schemas.audio_submission import AudioSubmissionCreate
from utils.whisper_transcriber import transcribe_audio_with_whisper

logger = logging.getLogger(__name__)

TEMP_FILES_DIR = "temp_audio"
os.makedirs(TEMP_FILES_DIR, exist_ok=True)

def get_db_session() -> Generator:
    db_gen = get_db()
    try:
        yield next(db_gen)
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass

async def save_telegram_file(telegram_file, user_id: int, extension: str) -> str:
    file_name = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(TEMP_FILES_DIR, file_name)
    await telegram_file.download_to_drive(file_path)
    logger.info(f"Temporary file saved: {file_path}")
    return file_path

async def _process_audio_transcription(
    update: Update,
    file_path: str,
    user_id: int,
    progress_message: Optional[Message] = None
):
    db_gen = get_db_session()
    db = next(db_gen)
    
    if progress_message is None:
        await update.message.chat.send_action("typing")
        progress_message = await update.message.reply_text("Processing your audio...")
    
    try:
        db_user = crud.get_user_by_telegram_id(db, user_id)
        if not db_user:
            user_data = UserCreateTelegram(
                telegram_id=user_id,
                username=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name,
                email=None,
                hashed_password=None
            )
            db_user = crud.create_telegram_user(db, user_data)
        
        transcription_result = transcribe_audio_with_whisper(file_path)
        transcription_text = transcription_result.get("text")
        detected_language = transcription_result.get("language")

        if transcription_text.startswith("Error") or transcription_text.startswith("Whisper transcription error"):
            raise Exception(transcription_text)
        
        if progress_message:
            try:
                await progress_message.delete()
                logger.info(f"Deleted progress message: {progress_message.message_id}")
            except Exception as e:
                logger.warning(f"Could not delete progress message {progress_message.message_id}: {e}")

        crud.create_audio_submission(
            db,
            submission=AudioSubmissionCreate(audio_path=file_path, original_transcript=transcription_text),
            user_id=db_user.id
        )
        
        output_message = (
            "Transcription Result\n"
            f"Language: {detected_language.upper()}\n"
            "\n"
            f"`{transcription_text}`" # Se envolvió el texto en backticks para hacerlo copiable
        )
        await update.message.reply_text(output_message, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error processing transcription for user {user_id}: {e}", exc_info=True)
        if progress_message:
            try:
                await progress_message.delete()
            except Exception as delete_e:
                logger.warning(f"Could not delete error-related progress message {progress_message.message_id}: {delete_e}")
        await update.message.reply_text(f"An error occurred while processing your message: {str(e)}")
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Temporary file deleted: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting temporary file {file_path}: {e}")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    audio_file = await update.message.audio.get_file()
    file_extension = Path(audio_file.file_path).suffix if audio_file.file_path else '.mp3'

    file_path = await save_telegram_file(audio_file, user_id, file_extension)
    await _process_audio_transcription(update, file_path, user_id)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    voice_file = await update.message.voice.get_file()
    file_extension = ".ogg"

    file_path = await save_telegram_file(voice_file, user_id, file_extension)
    await _process_audio_transcription(update, file_path, user_id)

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    message = update.message
    video_file = None
    video_extension = ".mp4"

    progress_message_for_video = None

    try:
        if message.video_note:
            video_file = await message.video_note.get_file()
            await context.bot.send_chat_action(chat_id=user_id, action="record_video")
            progress_message_for_video = await context.bot.send_message(user_id, "Processing your video...")
        elif message.video:
            video_file = await message.video.get_file()
            if message.video.mime_type and '/' in message.video.mime_type:
                video_extension = f".{message.video.mime_type.split('/')[-1]}"
            await context.bot.send_chat_action(chat_id=user_id, action="upload_video")
            progress_message_for_video = await context.bot.send_message(user_id, "Processing your video...")
        else:
            await context.bot.send_message(user_id, "Unrecognized video type.")
            return

        video_path = await save_telegram_file(video_file, user_id, video_extension)
        
        audio_path = os.path.join(TEMP_FILES_DIR, f"{uuid.uuid4()}.mp3")
        video_segment = AudioSegment.from_file(video_path)
        video_segment.export(audio_path, format="mp3")
        logger.info(f"Audio extracted to: {audio_path}")
        
        await _process_audio_transcription(update, audio_path, user_id, progress_message_for_video)

    except Exception as e:
        logger.error(f"Error processing video for user {user_id}: {e}", exc_info=True)
        if progress_message_for_video:
            try:
                await progress_message_for_video.delete()
            except Exception: pass
        await context.bot.send_message(user_id, f"An error occurred while processing your video: {str(e)}")
    finally:
        if 'video_path' in locals() and video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
                logger.info(f"Temporary video file deleted: {video_path}")
            except Exception as e:
                logger.error(f"Error deleting temporary video file {video_path}: {e}")
