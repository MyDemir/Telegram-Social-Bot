from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bot.telegram import start, set_source_group, set_target_group, set_twitter_target, forward_message
from bot.twitter import get_twitter_updates
from bot.config import TELEGRAM_BOT_TOKEN
from bot.utils import load_env

# .env dosyasındaki bilgileri yükle
load_env()

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Komutlar
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.command, set_source_group))  # Kaynak grup için
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.command, set_target_group))  # Hedef grup için
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.command, set_twitter_target))  # Twitter hedefi için
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.chat(chat_id='source_group_id'), forward_message))  # Mesaj aktarma

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
