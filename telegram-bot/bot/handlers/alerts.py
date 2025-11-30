"""Alerts command handler."""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /alerts command."""
    alerts_message = """
🔔 **Alert Configuration**

Current Settings:
✅ Payment notifications: ON
✅ Worker down alerts: ON
✅ High temperature warnings: ON
✅ Performance alerts: ON

You'll receive notifications when:
• Payment is received
• Worker goes offline
• GPU temperature > 85°C
• Error rate > 10%
    """

    await update.message.reply_text(alerts_message, parse_mode="Markdown")
