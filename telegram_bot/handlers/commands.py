import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from typing import Generator

from database.config import get_db
from database import crud # Necesitamos la función de CRUD para eliminar

logger = logging.getLogger(__name__)

def get_db_session() -> Generator[Session, None, None]:
    db_gen = get_db()
    try:
        yield next(db_gen)
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    keyboard = [[KeyboardButton("📜 My Audios")]] 
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I'm your Russian transcription assistant.",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
🤖 *Available Commands:*
/start - Start the bot
/help - Show this help
/my_audios - View your saved audio transcriptions
/delete_audio <ID> - Delete a specific audio transcription by its ID (e.g., `/delete_audio 123`)

🎙 *Features:*
- Send me a voice message, and I'll transcribe it
- Send me an audio file (MP3, WAV, etc.)
- Send me a video file or video note, and I'll transcribe it
"""
    await update.message.reply_markdown(help_text)

async def my_transcriptions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_telegram_id = update.effective_user.id
    logger.info(f"Attempting to retrieve transcriptions for Telegram user ID: {user_telegram_id}")

    db_gen = get_db_session()
    db = next(db_gen)
    try:
        db_user = crud.get_user_by_telegram_id(db, user_telegram_id)
        
        if not db_user:
            logger.warning(f"User with Telegram ID {user_telegram_id} not found in DB.")
            await update.message.reply_text("It looks like you don't have an account registered. Send an audio/video to create one.")
            return
        
        logger.info(f"Found DB user for Telegram ID {user_telegram_id}: User ID {db_user.id}")
        
        transcriptions = crud.get_audio_submissions_by_user(db, db_user.id)
        
        if not transcriptions:
            logger.info(f"No saved transcriptions found for user ID {db_user.id}.")
            await update.message.reply_text("You don't have any saved transcriptions yet.")
            return
        
        logger.info(f"Found {len(transcriptions)} transcriptions for user ID {db_user.id}.")
        response_text = "📜 **Your Recent Transcriptions:**\n\n"
        for submission in transcriptions:
            timestamp_str = submission.created_at.strftime("%d/%m/%Y %H:%M") if submission.created_at else "Unknown date"
            response_text += (
                f"**ID:** `{submission.id}`\n"
                f"*Timestamp:* `{timestamp_str}`\n"
                f"`{submission.original_transcript}`\n\n"
            )
        await update.message.reply_markdown(response_text)
    except Exception as e:
        logger.error(f"Error loading transcriptions for user {user_telegram_id}: {e}", exc_info=True)
        await update.message.reply_text("An error occurred while loading your transcriptions.")
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass

async def delete_audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_telegram_id = update.effective_user.id
    # Los argumentos del comando están en context.args
    if not context.args:
        await update.message.reply_text("Please provide the ID of the transcription you want to delete. Usage: `/delete_audio <ID>`")
        return

    try:
        submission_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid ID provided. Please enter a numerical ID.")
        return

    logger.info(f"Attempting to delete transcription ID {submission_id} for Telegram user ID: {user_telegram_id}")

    db_gen = get_db_session()
    db = next(db_gen)
    try:
        db_user = crud.get_user_by_telegram_id(db, user_telegram_id)
        if not db_user:
            logger.warning(f"User with Telegram ID {user_telegram_id} not found in DB, cannot delete.")
            await update.message.reply_text("You don't have an account registered. No transcriptions to delete.")
            return

        # Intentar borrar la transcripción
        # Esta función `delete_audio_submission` la crearemos en database/crud.py
        deleted = crud.delete_audio_submission(db, submission_id, db_user.id) 

        if deleted:
            logger.info(f"Successfully deleted transcription ID {submission_id} for user {db_user.id}.")
            await update.message.reply_text(f"Transcription with ID `{submission_id}` has been deleted.")
        else:
            logger.warning(f"Transcription ID {submission_id} not found or not owned by user {db_user.id}.")
            await update.message.reply_text(f"Transcription with ID `{submission_id}` not found or you don't have permission to delete it.")

    except Exception as e:
        logger.error(f"Error deleting transcription ID {submission_id} for user {user_telegram_id}: {e}", exc_info=True)
        await update.message.reply_text("An error occurred while trying to delete the transcription.")
    finally:
        try:
            next(db_gen)
        except StopIteration:
            pass

