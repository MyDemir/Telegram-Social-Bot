import os
from dotenv import load_dotenv
from telegram_bot import start, set_channels, forward_content  # doğru import ekledik
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# .env dosyasını yükleme
load_dotenv()

# Bot tokenini yükleme
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Bot tokeni bulunamadı. Lütfen .env dosyasına TELEGRAM_BOT_TOKEN ekleyin.")

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Komutlar
    application.add_handler(CommandHandler("start", start))  # start fonksiyonu burada kullanılıyor
    application.add_handler(CommandHandler("set_channels", set_channels))

    # Kanal mesajlarını dinleme
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_content))

    application.run_polling()

if __name__ == "__main__":
    main()
