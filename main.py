import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from telegram.error import BadRequest
import asyncio
from twitter import start_twitter_check_periodically
from telegram_bot import start, set_channels, add_twitter_user, forward_content, check_and_send_tweets

# .env dosyasını yükle
load_dotenv()

# Bot token'ını al
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Bot ve uygulama için log ayarları
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Asenkron Twitter kontrolünü başlatmak için async görev oluşturma
async def periodic_twitter_check():
    while True:
        await start_twitter_check_periodically()  # Twitter kontrol fonksiyonunu çalıştır
        await asyncio.sleep(60)  # 60 saniye bekle

async def main() -> None:
    """Botu başlatma ve komut işleyicilerini ekleme"""
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Komutlar ve işleyiciler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))
    application.add_handler(CommandHandler("add_twitter", add_twitter_user))
    
    # Kanal mesajlarını dinlemek ve yönlendirmek için handler
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_content))

    # Twitter'dan gelen tweetleri kontrol etme ve yönlendirme
    application.add_handler(CommandHandler("check_twitter", check_and_send_tweets))

    # Job queue başlatma - Zaten asenkron olarak twitter kontrolü yapılacak
    job_queue = application.job_queue
    job_queue.run_repeating(periodic_twitter_check, interval=60, first=0)

    # Uygulamayı çalıştır
    await application.run_polling()

if __name__ == "__main__":
    # Bu satırı kaldırıyoruz çünkü application.run_polling() kendi event loop'unu yönetiyor
    asyncio.run(main())  # Burayı kaldırarak hatayı engellemiş olduk
