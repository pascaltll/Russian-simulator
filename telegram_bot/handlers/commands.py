"""
Telegram bot command handlers.

This module provides functions to handle various commands sent to the bot,
including starting the bot, showing help, displaying user transcriptions,
and deleting specific audio submissions.
"""

# Group 1: Standard libraries
import logging
from typing import Generator

# Group 2: Third-party libraries
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Group 3: First-party modules
from database.config import get_db
from database import crud

logger = logging.getLogger(__name__)


def get_db_session() -> Generator[Session, None, None]:
    """
    Provides a database session for Telegram handler functions.
    """
    yield from get_db()


async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command. Greets the user and shows a custom keyboard.
    """
    user = update.effective_user
    keyboard = [[KeyboardButton("📜 My Audios")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I'm your Russian transcription assistant.",
        reply_markup=reply_markup
    )


async def help_command(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /help command. Sends a list of available commands and features.
    """
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


async def my_transcriptions_command(
    update: Update, _context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handles the /my_audios command. Lists user's audio transcriptions.
    """
    user_telegram_id = update.effective_user.id
    logger.info(
        "Attempting to retrieve transcriptions for Telegram user ID: %s",
        user_telegram_id
    )

    db_session_gen = get_db_session()
    db = next(db_session_gen)
    try:
        db_user = crud.get_user_by_telegram_id(db, user_telegram_id)

        if not db_user:
            logger.warning(
                "User with Telegram ID %s not found in DB.",
                user_telegram_id
            )
            await update.message.reply_text(
                "It looks like you don't have an account registered. "
                "Send an audio/video to create one."
            )
            return

        logger.info(
            "Found DB user for Telegram ID %s: User ID %s",
            user_telegram_id, db_user.id
        )

        transcriptions = crud.get_audio_submissions_by_user(db, db_user.id)

        if not transcriptions:
            logger.info(
                "No saved transcriptions found for user ID %s.",
                db_user.id
            )
            await update.message.reply_text(
                "You don't have any saved transcriptions yet."
            )
            return

        logger.info(
            "Found %d transcriptions for user ID %s.",
            len(transcriptions), db_user.id
        )
        response_text = "📜 **Your Recent Transcriptions:**\n\n"
        for submission in transcriptions:
            timestamp_str = (
                submission.created_at.strftime("%d/%m/%Y %H:%M")
                if submission.created_at else "Unknown date"
            )
            response_text += (
                f"**ID:** `{submission.id}`\n"
                f"*Timestamp:* `{timestamp_str}`\n"
                f"`{submission.original_transcript}`\n\n"
            )
        await update.message.reply_markdown(response_text)

    except SQLAlchemyError as exc:
        logger.error(
            "DB error while loading transcriptions for user %s: %s",
            user_telegram_id, exc, exc_info=True
        )
        await update.message.reply_text(
            "A database error occurred while loading your transcriptions."
        )

    finally:
        pass  # Session closed automatically by get_db()


async def delete_audio_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handles the /delete_audio <ID> command. Deletes a user's transcription by ID.
    """
    user_telegram_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text(
            "Please provide the ID of the transcription you want to delete. "
            "Usage: `/delete_audio <ID>`"
        )
        return

    try:
        submission_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "Invalid ID provided. Please enter a numerical ID."
        )
        return

    logger.info(
        "Attempting to delete transcription ID %s for Telegram user ID: %s",
        submission_id, user_telegram_id
    )

    db_session_gen = get_db_session()
    db = next(db_session_gen)
    try:
        db_user = crud.get_user_by_telegram_id(db, user_telegram_id)
        if not db_user:
            logger.warning(
                "User with Telegram ID %s not found in DB, cannot delete.",
                user_telegram_id
            )
            await update.message.reply_text(
                "You don't have an account registered. No transcriptions to delete."
            )
            return

        deleted = crud.delete_audio_submission(db, submission_id, db_user.id)

        if deleted:
            logger.info(
                "Successfully deleted transcription ID %s for user %s.",
                submission_id, db_user.id
            )
            await update.message.reply_text(
                f"Transcription with ID `{submission_id}` has been deleted."
            )
        else:
            logger.warning(
                "Transcription ID %s not found or not owned by user %s.",
                submission_id, db_user.id
            )
            await update.message.reply_text(
                f"Transcription with ID `{submission_id}` not found or you don't "
                "have permission to delete it."
            )

    except SQLAlchemyError as exc:
        logger.error(
            "DB error deleting transcription ID %s for user %s: %s",
            submission_id, user_telegram_id, exc, exc_info=True
        )
        await update.message.reply_text(
            "A database error occurred while trying to delete the transcription."
        )

    finally:
        pass  # Session closed automatically by get_db()
