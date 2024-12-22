from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.filters import Text  # Filters yerine Text kullanıyoruz
from telegram import Bot
from telegram.ext import Application  # Application importunu ekliyoruz
import os
from dotenv import load_dotenv
from get_x_updates import get_x_updates

# .env dosyasını yükleyelim
load_dotenv()

# Telegram Bot Token'ı
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Telegram Botunu Başlat
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Hedef kanalın ID'sini buraya yazıyoruz (başka bir grup veya kanal)
TARGET_CHANNEL_ID = '@your_target_channel_or_group'

# X güncellemelerini Telegram kanalına gönder
async def send_updates(update, context):
    # Kullanıcının yazdığı tweet kullanıcısının adı
    username = context.args[0]

    updates = get_x_updates(username)

    # Kullanıcıya güncellemeleri gönder
    await context.bot.send_message(chat_id=update.effective_chat.id, text=updates)

# Mesajları dinle ve ilet
async def forward_message(update, context):
    await context.bot.forward_message(chat_id=TARGET_CHANNEL_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)

# Komutları ekleyelim
send_updates_handler = CommandHandler('getupdates', send_updates)
application.add_handler(send_updates_handler)

# Mesajları dinle
message_handler = MessageHandler(Text & ~Filters.command, forward_message)
application.add_handler(message_handler)

# Botu başlat
application.run_polling()
