from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from x_updates import send_updates
from telegram_forward import forward_message
from config import TELEGRAM_BOT_TOKEN

# Botu başlatma
def start(update, context):
    update.message.reply_text("Bot çalışıyor! İçerik kanalını ve hedef kanalınızı seçin.")

def main():
    # Botu başlatıyoruz
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Başlangıç komutu
    dispatcher.add_handler(CommandHandler('start', start))

    # X platformundan güncellemeleri alma
    dispatcher.add_handler(CommandHandler('get_x_updates', send_updates))

    # Mesaj kopyalama
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_message))

    # Polling başlatma
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
