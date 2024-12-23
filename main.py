import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram_bot import start, set_channels, set_twitter, send_channel_update_notification

def main():
    load_dotenv()

    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("Bot tokeni bulunamadı. .env dosyasına TELEGRAM_BOT_TOKEN ekleyin.")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("test_twitter", test_twitter))
    # Komutları ekle
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))
    application.add_handler(CommandHandler("set_twitter", set_twitter))

    # Kanal mesaj bildirimleri
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, send_channel_update_notification))

    application.run_polling()

if __name__ == "__main__":
    main()
