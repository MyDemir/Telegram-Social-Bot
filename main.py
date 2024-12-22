import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.error import TelegramError
from x_updates import get_twitter_updates

# .env dosyasındaki bilgileri yükle
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# '/start' komutu
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Merhaba! Ben Telegram Social Bot V2.\nTwitter güncellemelerini almak için /get_x_updates [kullanıcı_adı] komutunu kullanabilirsiniz.')

# '/get_x_updates' komutu
def get_updates(update: Update, context: CallbackContext) -> None:
    if len(context.args) > 0:
        username = context.args[0]
        updates = get_twitter_updates(username)
        
        # Eğer tweetler varsa, bunları Telegram'a gönderiyoruz
        if "Hata" not in updates:
            try:
                update.message.reply_text(updates)  # Tweet içeriklerini Telegram'a gönder
            except TelegramError as e:
                update.message.reply_text(f"Telegram hatası: {e}")
        else:
            update.message.reply_text(updates)  # Eğer hata varsa, hata mesajını gönder
    else:
        update.message.reply_text('Lütfen bir kullanıcı adı girin.')

# Botu başlatma
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("get_x_updates", get_updates))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
