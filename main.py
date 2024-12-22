from telegram_bot import start, set_source_group, set_target_group, set_twitter_target, forward_twitter_updates
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bot.config import TELEGRAM_BOT_TOKEN

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)

    dp = updater.dispatcher

    # Komutlar ve mesaj işleyicilerinin eklenmesi
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, set_source_group))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, set_target_group))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, set_twitter_target))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_twitter_updates))

    # Botun çalıştırılması
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
