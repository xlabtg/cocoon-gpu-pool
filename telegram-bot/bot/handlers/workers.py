"""Workers command handler."""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def workers_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /workers command."""
    # TODO: Fetch workers from API
    workers_message = """
🔧 **Your GPU Workers**

**Worker-0** (Instance 0)
Status: 🟢 Healthy
GPU Util: 92%
Temp: 68°C
Revenue: 65.30 TON

**Worker-1** (Instance 1)
Status: 🟢 Healthy
GPU Util: 82%
Temp: 71°C
Revenue: 60.20 TON
    """

    await update.message.reply_text(workers_message, parse_mode="Markdown")
