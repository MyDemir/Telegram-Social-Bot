import os
import asyncio
from dotenv import load_dotenv
from telegram_bot import start, set_channels, forward_content, add_twitter_user
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from twitter import send_tweet_to_channel

# .env dosyasını yükleme
load_dotenv()

# Bot tokenini yükleme
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Bot tokeni bulunamadı. Lütfen .env dosyasına TELEGRAM_BOT_TOKEN ekleyin.")

async def start_twitter_check_periodically(update, context):
    while True:
        user_info = load_user_info()
        for user_id, info in user_info.items():
            if "twitter_username" in info:
                twitter_username = info["twitter_username"]
                target_channel = info["target_channel"]
                # Son tweet'i kontrol et ve hedef kanala gönder
                await send_tweet_to_channel(update, context, twitter_username, target_channel)
        await asyncio.sleep(1800)  # 30 dakika bekle

async def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Komutlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))
    application.add_handler(CommandHandler("add_twitter", add_twitter_user))

    # Kanal mesajlarını dinleme
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_content))

    # Asenkron işlemi başlat
    asyncio.create_task(start_twitter_check_periodically())  # Twitter kontrolünü başlat

    # Uygulamayı çalıştır
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
