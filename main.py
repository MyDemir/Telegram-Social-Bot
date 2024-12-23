import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from twitter import handle_twitter_updates

# .env dosyasını yükleme
load_dotenv()

# Bot tokenini yükleme
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Bot tokeni bulunamadı. Lütfen .env dosyasına TELEGRAM_BOT_TOKEN ekleyin.")

# Kullanıcı bilgilerini saklamak için
user_info = {}

# Twitter kullanıcı adı ayarlama komutu
async def set_twitter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if len(context.args) != 1:
        await update.message.reply_text("Lütfen bir Twitter kullanıcı adı girin. Örnek: /set_twitter elonmusk")
        return
    
    twitter_user = context.args[0]

    # Kullanıcının Twitter bilgilerini kaydet
    user_info[user_id] = {
        "twitter_user": twitter_user
    }
    await update.message.reply_text(f"Başarıyla Twitter kullanıcı adınız {twitter_user} olarak kaydedildi!")

# X (Twitter) güncellemelerini almak için komut
async def get_twitter_updates_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    if user_id not in user_info or "twitter_user" not in user_info[user_id]:
        await update.message.reply_text("Lütfen önce bir Twitter kullanıcı adı belirleyin. Örnek: /set_twitter elonmusk")
        return

    twitter_target = user_info[user_id]["twitter_user"]

    # Twitter güncellemelerini twitter.py dosyasından al
    twitter_updates = handle_twitter_updates(user_id, twitter_target)

    # Tweet'leri Telegram'a gönder
    await update.message.reply_text(twitter_updates)

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Komutlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))
    application.add_handler(CommandHandler("set_twitter", set_twitter))  # Yeni komut
    application.add_handler(CommandHandler("get_twitter_updates", get_twitter_updates_command))  # Yeni komut

    # Kanal mesajlarını dinleme
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_content))

    application.run_polling()

if __name__ == "__main__":
    main()

"""import os
from dotenv import load_dotenv
from telegram_bot import start, set_channels, forward_content
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
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))

    # Kanal mesajlarını dinleme
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_content))

    application.run_polling()

if __name__ == "__main__":
    main()
"""
