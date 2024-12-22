import os
from dotenv import load_dotenv
from telegram_bot import start, set_channels, forward_messages, forward_twitter_updates
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

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
    
    # Text mesajlarını alıyoruz, fakat komutları manuel olarak kontrol ediyoruz
    application.add_handler(MessageHandler(filters.TEXT, lambda update, context: handle_message_if_not_command(update, context)))
    
    application.add_handler(CommandHandler("forward_twitter_updates", forward_twitter_updates))

    # Botu çalıştır
    await application.run_polling()

async def handle_message_if_not_command(update: Update, context):
    if not update.message.text.startswith('/'):  # Komutla başlamayan mesajlar için
        await forward_messages(update, context)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
