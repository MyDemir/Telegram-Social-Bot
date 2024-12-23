import os
from dotenv import load_dotenv
from telegram_bot import start, set_channels, forward_messages, connect_channels
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# .env dosyasını yükleme
load_dotenv()

# TELEGRAM_BOT_TOKEN çevresel değişkeninden bot tokenini al
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Bot tokeni .env dosyasından alınamadı. Lütfen TELEGRAM_BOT_TOKEN değeri ekleyin.")

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handler'lar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))
    application.add_handler(CommandHandler("connect", connect_channels))  # /connect komutu
    
    # Tüm mesajları alıp iletme
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_messages))

    application.run_polling()

if __name__ == "__main__":
    main()
