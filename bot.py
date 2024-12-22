import telegram
import time
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from twitter_bot import get_twitter_updates
from discord_bot import get_discord_updates
from youtube_bot import get_youtube_updates

# Telegram bot token'ınızı buraya ekleyin
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Loglama ayarları
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Telegram bot mesaj gönderme fonksiyonu
def send_message(update, context, message):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text=message)

# Kullanıcıdan gelen mesajlara tepki
def start(update, context):
    send_message(update, context, "Merhaba! Ben Telegram Social Bot. Twitter, Discord, YouTube gibi platformlardaki güncellemeleri alıp buraya aktarıyorum.")

# Ana fonksiyon
def main():
    # Komutları bağla
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    
    # Botu başlat
    updater.start_polling()
    updater.idle()

# Botu çalıştır
if __name__ == '__main__':
    main()
