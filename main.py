import os
from dotenv import load_dotenv
from telegram_bot import start, set_channels, forward_messages, forward_twitter_updates
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import asyncio

# .env dosyasını yükleme
load_dotenv()

# TELEGRAM_BOT_TOKEN çevresel değişkeninden bot tokenini al
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Bot tokeni .env dosyasından alınamadı. Lütfen TELEGRAM_BOT_TOKEN değeri ekleyin.")

async def main() -> None:
    # Telegram botunun token'ını .env dosyasından alıyoruz
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handler'lar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))
    
    # Text mesajlarını, ancak komutları dışarıda bırakacak şekilde ekliyoruz
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_messages))

    # Twitter güncellemeleri iletme komutunu ekliyoruz
    application.add_handler(CommandHandler("forward_twitter_updates", forward_twitter_updates))

    # Botu çalıştır
    await application.run_polling()

if __name__ == "__main__":
    # asyncio.run yerine doğrudan asyncio event loop ile çalışıyoruz
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
