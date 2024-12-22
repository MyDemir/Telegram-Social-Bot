import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from x_bot import get_x_updates  # 'twitter_bot.py' yerine 'x_bot.py' olacak
from telegram_send import send_message

# Telegram bot token'ınızı buraya ekleyin
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Loglama ayarları
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Durum kodları
GET_USERNAME = 1
GET_SOURCE_CHANNEL = 2
GET_TARGET_CHANNEL = 3

# Telegram bot mesaj gönderme fonksiyonu
def send_message(update, context, message):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text=message)

# Kullanıcıdan gelen mesajlara tepki
def start(update, context):
    send_message(update, context, "Merhaba! Ben Telegram Social Bot. X'ten gelen güncellemeleri burada alabilirsin.")
    send_message(update, context, "Lütfen takip etmek istediğiniz X kullanıcı adını gönderin.")
    return GET_USERNAME

# Kullanıcıdan X kullanıcı adını alma
def get_username(update, context):
    x_username = update.message.text.strip()  # Kullanıcı adını al
    send_message(update, context, f"Takip ediyorum: {x_username}. Bir saniye...")
    updates = get_x_updates(x_username)  # Kullanıcının X'teki güncellemelerini al
    send_message(update, context, updates)  # Telegram'a gönder
    return ConversationHandler.END

# Kaynak kanal/grup bilgisini alma
def get_source_channel(update, context):
    source_channel_id = update.message.text.strip()
    context.user_data['source_channel'] = source_channel_id
    send_message(update, context, f"Kaynak kanal/grup: {source_channel_id}. Şimdi hedef kanal/grup ID'sini girin.")
    return GET_TARGET_CHANNEL

# Hedef kanal/grup bilgisini alma
def get_target_channel(update, context):
    target_channel_id = update.message.text.strip()
    context.user_data['target_channel'] = target_channel_id
    send_message(update, context, f"Hedef kanal/grup: {target_channel_id}. Mesaj aktarımına başlıyoruz!")
    transfer_messages(update, context)
    return ConversationHandler.END

# Kaynak kanaldan mesajları alıp hedef kanala aktaran fonksiyon
def transfer_messages(update, context):
    source_channel_id = context.user_data['source_channel']
    target_channel_id = context.user_data['target_channel']
    
    # Burada, kaynak kanaldan alınan mesajlar hedef kanala aktarılacak.
    context.bot.send_message(chat_id=target_channel_id, text="Mesaj aktarımı başarılı!")
    
    send_message(update, context, f"Mesajlar {target_channel_id} kanalına aktarılmıştır!")

# İptal etme işlemi
def cancel(update, context):
    send_message(update, context, "İşlem iptal edildi.")
    return ConversationHandler.END

# Ana fonksiyon
def main():
    # Komutları bağla
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    # Kaynak ve hedef kanal/grup ID'sini alma işlemi
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GET_USERNAME: [MessageHandler(Filters.text & ~Filters.command, get_username)],
            GET_SOURCE_CHANNEL: [MessageHandler(Filters.text & ~Filters.command, get_source_channel)],
            GET_TARGET_CHANNEL: [MessageHandler(Filters.text & ~Filters.command, get_target_channel)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)

    # Botu başlat
    updater.start_polling()
    updater.idle()

# Botu çalıştır
if __name__ == '__main__':
    main()
