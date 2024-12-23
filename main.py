import os
from telegram import Update
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from telegram_bot import start, set_channels, forward_content, notify_twitter_update, set_twitter

def main():
    # .env dosyasını yükleme
    load_dotenv()

    # Bot tokenini yükleme
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("Bot tokeni bulunamadı. Lütfen .env dosyasına TELEGRAM_BOT_TOKEN ekleyin.")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Komutları ekle
    application.add_handler(CommandHandler("start", start))  # Başlat komutu
    application.add_handler(CommandHandler("set_channels", set_channels))  # Kanal ayarları
    application.add_handler(CommandHandler("set_twitter", set_twitter))  # Twitter kullanıcı adını ayarlama
    application.add_handler(CommandHandler("notify_twitter_update", notify_twitter_update))  # Twitter bildirimleri
    application.add_handler(CommandHandler("forward_content", forward_content))  # Kanal içeriği yönlendirme

    # Uygulamayı başlat
    application.run_polling()

if __name__ == "__main__":
    main()
