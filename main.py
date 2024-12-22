from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging
from get_x_updates import get_x_updates
from forward_message import forward_message
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# .env dosyasından TELEGRAM_BOT_TOKEN'ı al
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Botu başlatmak için gerekli ayarlar
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Botu başlat
application.run_polling()

# '/start' komutu
async def start(update: Update, context):
    await update.message.reply_text("Bot çalışıyor! X (Twitter) kullanıcı adı girerek güncellemeleri alabilirsiniz.")

# '/get_updates' komutu, X (Twitter) güncellemelerini almak için
async def get_updates(update: Update, context):
    if len(context.args) == 0:
        await update.message.reply_text("Lütfen bir X (Twitter) kullanıcı adı girin.")
        return

    username = context.args[0]
    updates = get_x_updates(username)
    await update.message.reply_text(updates)

# Komutları ekleyelim
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('get_updates', get_updates))
application.add_handler(MessageHandler(filters.TEXT, forward_message))

# Loglama yapılandırması
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
