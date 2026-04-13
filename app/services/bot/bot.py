from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging
import sys
import httpx

from app.core.config import settings

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

welcome_message = "Welcome to the bot! Use /start to start the app."

API_URL = "http://localhost:8000/api/v1"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f"User {user.id} started the bot.")

    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{API_URL}/users", json={
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            })
    except Exception as e:
        logger.error(f"Failed to upsert user {user.id}: {e}")

    keyboard = [
        [InlineKeyboardButton("open mini app", web_app=WebAppInfo(url="https://nonplacental-unprecipitantly-brigid.ngrok-free.dev/ui"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


app = ApplicationBuilder().token(settings.BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
