"""Stats command handler."""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /stats command."""
    # TODO: Fetch stats from API
    stats_message = """
📊 **Your Statistics**

🔧 Active Workers: 2
💰 Total Revenue: 125.50 TON
📈 Avg GPU Utilization: 87%
⚡ Total Requests: 15,234

_Last updated: 5 minutes ago_
    """

    await update.message.reply_text(stats_message, parse_mode="Markdown")
