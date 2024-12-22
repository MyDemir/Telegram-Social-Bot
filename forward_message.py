from telegram import Bot
from telegram.ext import CommandHandler, MessageHandler, filters, Application
import os
from dotenv import load_dotenv

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
def send_updates(update, context):
    # Kullanıcının yazdığı tweet kullanıcısının adı
    username = context.args[0]
    
    # get_x_updates fonksiyonu burada kullanılacak
    updates = get_x_updates(username)
    
    # Kullanıcıya güncellemeleri gönder
    context.bot.send_message(chat_id=update.effective_chat.id, text=updates)

# Mesajları dinle ve ilet
def forward_message(update, context):
    context.bot.forward_message(chat_id=TARGET_CHANNEL_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)

# Komutları ekleyelim
send_updates_handler = CommandHandler('getupdates', send_updates)
application.add_handler(send_updates_handler)

# Mesajları dinle
message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message)
application.add_handler(message_handler)

# Botu başlat
application.run_polling()
