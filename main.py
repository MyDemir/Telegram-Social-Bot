"""import os
from dotenv import load_dotenv
from telegram_bot import start, set_channels, forward_messages, forward_twitter_updates
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# .env dosyasını yükleme
load_dotenv()

# TELEGRAM_BOT_TOKEN çevresel değişkeninden bot tokenini al
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Bot tokeni .env dosyasından alınamadı. Lütfen TELEGRAM_BOT_TOKEN değeri ekleyin.")

def main() -> None:
    # Telegram botunun token'ını .env dosyasından alıyoruz
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handler'lar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))
    
    # Text mesajlarını alıyoruz, fakat komutları hariç tutuyoruz
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_messages))
    
    application.add_handler(CommandHandler("forward_twitter_updates", forward_twitter_updates))

    # Botu çalıştır
    application.run_polling()

if __name__ == "__main__":
    main()
    """
import os
from dotenv import load_dotenv
from telegram_bot import start, forward_messages
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# .env dosyasını yükleme
load_dotenv()

# TELEGRAM_BOT_TOKEN çevresel değişkeninden bot tokenini al
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Bot tokeni .env dosyasından alınamadı. Lütfen TELEGRAM_BOT_TOKEN değeri ekleyin.")

def main() -> None:
    # Telegram botunun token'ını .env dosyasından alıyoruz
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handler'lar
    application.add_handler(CommandHandler("start", start))
    
    # Text mesajlarını alıyoruz, fakat komutları hariç tutuyoruz
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_messages))

    # Botu çalıştır
    application.run_polling()

if __name__ == "__main__":
    main()
