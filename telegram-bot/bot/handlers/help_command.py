"""Help command handler."""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command."""
    help_message = """
ℹ️ **Cocoon GPU Pool Bot Help**

**Commands:**
/start - Initialize your account
/stats - View your statistics
/payouts - View payout history
/workers - Manage GPU workers
/alerts - Configure notifications
/help - Show this help message

**Support:**
Join our Telegram community: @xlab_tg

**Documentation:**
https://cocoon.org/gpu-owners

Need help? Contact our support team through the community channel.
    """

    await update.message.reply_text(help_message, parse_mode="Markdown")
