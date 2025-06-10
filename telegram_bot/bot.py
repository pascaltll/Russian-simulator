"""
Main entry point for the Telegram bot application.

This module initializes the Telegram bot, registers all command and message handlers,
and starts the polling mechanism to listen for incoming updates.
It also configures logging and handles environment variables.
"""

# Group 1: Standard libraries
import asyncio
import logging
import os
import sys

# Group 2: Third-party libraries
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Modify sys.path **after** imports are declared to avoid Pylint C0413 errors
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Group 3: First-party modules
from telegram_bot.handlers.commands import (
    start,
    help_command,
    my_transcriptions_command,
    delete_audio_command,
)
from telegram_bot.handlers.audio_handler import (
    handle_audio,
    handle_voice,
    handle_video,
)

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


async def main():
    """
    Initializes and runs the Telegram bot.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error(
            "TELEGRAM_BOT_TOKEN environment variable not set. "
            "Please set it to run the bot."
        )
        raise ValueError("TELEGRAM_BOT_TOKEN not found.")

    application = Application.builder().token(bot_token).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("my_audios", my_transcriptions_command))
    application.add_handler(CommandHandler("delete_audio", delete_audio_command))

    # Register message handlers
    application.add_handler(
        MessageHandler(filters.AUDIO & ~filters.COMMAND, handle_audio)
    )
    application.add_handler(
        MessageHandler(filters.VOICE & ~filters.COMMAND, handle_voice)
    )
    application.add_handler(
        MessageHandler(filters.VIDEO | filters.VIDEO_NOTE, handle_video)
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.Regex(r'📜 My Audios'),
            my_transcriptions_command
        )
    )

    logger.info("Bot started. Listening for messages...")

    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down bot...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
    finally:
        if not loop.is_closed():
            loop.close()
