"""Cocoon GPU Pool Telegram Bot."""
import logging
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from .handlers import (
    start,
    stats,
    payouts,
    workers,
    alerts,
    help_command,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot."""
    # Get bot token from environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    # Create the Application
    application = Application.builder().token(token).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(CommandHandler("stats", stats.stats_command))
    application.add_handler(CommandHandler("payouts", payouts.payouts_command))
    application.add_handler(CommandHandler("workers", workers.workers_command))
    application.add_handler(CommandHandler("alerts", alerts.alerts_command))
    application.add_handler(CommandHandler("help", help_command.help_command))

    # Start the bot
    logger.info("Starting Cocoon GPU Pool Telegram Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
