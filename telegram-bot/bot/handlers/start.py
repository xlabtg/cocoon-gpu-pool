"""Start command handler."""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..services.api_client import APIClient

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    user = update.effective_user
    telegram_user_id = user.id

    logger.info(f"User {telegram_user_id} started the bot")

    welcome_message = f"""
👋 Welcome to Cocoon GPU Pool, {user.first_name}!

This bot helps you manage your GPU pool participation and monitor performance.

**Available Commands:**
/stats - View your statistics
/payouts - View payout history
/workers - Manage your GPU workers
/alerts - Configure notifications
/help - Get help

To get started, please connect your TON wallet address by sending it to me.
Example: `UQAbc...xyz`
    """

    await update.message.reply_text(welcome_message, parse_mode="Markdown")
