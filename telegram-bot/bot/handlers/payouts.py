"""Payouts command handler."""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def payouts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /payouts command."""
    # TODO: Fetch payouts from API
    payouts_message = """
💸 **Recent Payouts**

• 2025-01-15: 25.50 TON ✅
• 2025-01-08: 30.20 TON ✅
• 2025-01-01: 19.80 TON ✅

📊 Total Received: 125.50 TON
    """

    await update.message.reply_text(payouts_message, parse_mode="Markdown")
