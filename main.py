# main.py
import os
from dotenv import load_dotenv
from telegram_bot import start  # telegram_bot.py'dan start fonksiyonunu import et
from telegram.ext import ApplicationBuilder, CommandHandler

# .env dosyasını yükleme
load_dotenv()

# Bot tokenini yükleme
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Bot tokeni bulunamadı. Lütfen .env dosyasına TELEGRAM_BOT_TOKEN ekleyin.")

def help_message() -> str:
    return (
        "Merhaba! Botun komutları şunlardır:\n\n"
        "/start - Botu başlatır ve komutları gösterir.\n"
        "/set_channels <kaynak_kanal> <hedef_kanal> - Kaynak ve hedef kanalları ayarlayın.\n"
        "/set_twitter <kullanıcı_adı> - Twitter hesabını ayarlayın.\n\n"
        "Bot, kaynak kanaldan gelen içerikleri hedef kanalda paylaşacak ve Twitter'dan güncellemeler alacaktır."
    )

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Komutlar
    application.add_handler(CommandHandler("start", start))  # start komutunu telegram_bot.py'dan kullan
    application.add_handler(CommandHandler("help", help_message))  # help komutu ile yardım mesajını gönderir

    # Uygulamayı başlat
    application.run_polling()

if __name__ == "__main__":
    main()
