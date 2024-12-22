import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
from dotenv import load_dotenv
from get_x_updates import get_x_updates
from forward_message import forward_message

# .env dosyasını yükle
load_dotenv()

# .env dosyasından TELEGRAM_BOT_TOKEN'ı al
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Botu başlatmak için gerekli ayarlar
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

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

# Mesajı iletmek için mesaj işleyici
async def forward_message(update: Update, context):
    await context.bot.forward_message(chat_id='@your_target_channel_or_group',
                                      from_chat_id=update.message.chat_id,
                                      message_id=update.message.message_id)

# Komutları ekleyelim
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('get_updates', get_updates))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))

# Botu başlat
if __name__ == "__main__":
    # async run_polling'yi başlatmak için asyncio kullanıyoruz
    asyncio.run(application.run_polling())
