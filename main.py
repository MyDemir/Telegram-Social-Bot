import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from telegram.ext import Application
from telegram.ext import JobQueue
from telegram.error import BadRequest
from telegram_bot import start, set_channels, add_twitter_user, forward_content, check_and_send_tweets, load_user_info
import asyncio

# .env dosyasını yükle
load_dotenv()

# Bot token'ını al
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Bot ve uygulama için log ayarları
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_twitter_check_periodically(context: ContextTypes.DEFAULT_TYPE):
    """Twitter'ı periyodik olarak kontrol et"""
    await check_and_send_tweets(context)

async def main() -> None:
    """Botu başlatma ve komut işleyicilerini ekleme"""
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Komutlar ve işleyiciler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))
    application.add_handler(CommandHandler("add_twitter", add_twitter_user))
    
    # Kanal mesajlarını dinlemek ve yönlendirmek için handler
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_content))

    # Job queue başlatma
    job_queue = application.job_queue
    job_queue.run_repeating(start_twitter_check_periodically, interval=60, first=0)

    # Uygulamayı çalıştır
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
