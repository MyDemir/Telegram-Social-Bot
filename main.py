import os
from dotenv import load_dotenv
from telegram_bot import start, set_channels, set_twitter  # telegram_bot.py'dan fonksiyonları import et
from telegram.ext import ApplicationBuilder, CommandHandler

# .env dosyasını yükleme
load_dotenv()

# Bot tokenini yükleme
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Bot tokeni bulunamadı. Lütfen .env dosyasına TELEGRAM_BOT_TOKEN ekleyin.")

async def help_message(update, context):
    """Kullanıcılara komutları gösterir."""
    await update.message.reply_text(
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
    application.add_handler(CommandHandler("help", help_message))  # help komutunu ekle
    application.add_handler(CommandHandler("set_channels", set_channels))  # /set_channels komutunu ekle
    application.add_handler(CommandHandler("set_twitter", set_twitter))  # /set_twitter komutunu ekle

    # Uygulamayı başlat
    application.run_polling()

if __name__ == "__main__":
    main()
