import os
import asyncio
from dotenv import load_dotenv
from telegram_bot import start, set_channels, forward_content, add_twitter_user
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from twitter import start_twitter_check_periodically

# .env dosyasını yükleme
load_dotenv()

# Bot tokenini yükleme
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Bot tokeni bulunamadı. Lütfen .env dosyasına TELEGRAM_BOT_TOKEN ekleyin.")

async def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Komutlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))
    application.add_handler(CommandHandler("add_twitter", add_twitter_user))

    # Kanal mesajlarını dinleme
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_content))

    # Asenkron işlemi başlat
    # Twitter kontrolünü başlatıyoruz
    application.job_queue.run_repeating(start_twitter_check_periodically, interval=60, first=0)

    # Uygulamayı çalıştır
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
