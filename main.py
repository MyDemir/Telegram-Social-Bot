from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
import logging
from get_x_updates import get_x_updates
from forward_message import forward_message

# Botu başlatmak için gerekli ayarlar
updater = Updater(token='7520250082:AAGvNgm1KyT6-lmONaHvRKusMKhX3sGp-pM', use_context=True)
dispatcher = updater.dispatcher

# Botu başlat
updater.start_polling()

# '/start' komutu
def start(update, context):
    update.message.reply_text("Bot çalışıyor! X (Twitter) kullanıcı adı girerek güncellemeleri alabilirsiniz.")

# '/get_updates' komutu, X (Twitter) güncellemelerini almak için
def get_updates(update, context):
    if len(context.args) == 0:
        update.message.reply_text("Lütfen bir X (Twitter) kullanıcı adı girin.")
        return

    username = context.args[0]
    updates = get_x_updates(username)
    update.message.reply_text(updates)

# Mesajı iletmek için mesaj işleyici
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('get_updates', get_updates))
dispatcher.add_handler(MessageHandler(Filters.text, forward_message))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
