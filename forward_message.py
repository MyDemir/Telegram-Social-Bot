from telegram import Update
from telegram.ext import CallbackContext
from telegram.error import TelegramError
from bot.twitter import get_twitter_updates
from bot.config import TELEGRAM_BOT_TOKEN

user_info = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Merhaba! Ben Telegram Social Bot V2.\n'
                              'Mesaj aktarımı yapmak için önce kaynak ve hedef grup bilgilerini vereceksiniz.\n'
                              'Ayrıca Twitter kullanıcı adı ya da hashtag girerek, Twitter güncellemelerini de alabilirsiniz.\n'
                              'Lütfen önce kaynak grup ID\'sini girin.')

def set_source_group(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    source_group_id = update.message.text
    user_info[user_id] = {'source_group': source_group_id}
    
    update.message.reply_text(f"Kaynak grup {source_group_id} olarak ayarlandı. Şimdi hedef grup ID'sini girin.")

def set_target_group(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info:
        update.message.reply_text('Lütfen önce kaynak grup ID\'sini girin.')
        return

    target_group_id = update.message.text
    user_info[user_id]['target_group'] = target_group_id

    update.message.reply_text(f"Hedef grup {target_group_id} olarak ayarlandı.\n"
                              "Şimdi Twitter kullanıcı adı veya hashtag girin (örneğin: @username veya #hashtag).")

def set_twitter_target(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info:
        update.message.reply_text('Lütfen önce kaynak ve hedef grup ID\'lerini ayarlayın.')
        return

    twitter_target = update.message.text
    user_info[user_id]['twitter_target'] = twitter_target

    update.message.reply_text(f"Twitter hedefi {twitter_target} olarak ayarlandı.\n"
                              "Artık bu Twitter hedefine ait güncellemeleri alabiliriz.")

def forward_twitter_updates(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info:
        update.message.reply_text('Lütfen önce kaynak, hedef grup ve Twitter hedefi bilgilerini ayarlayın.')
        return

    twitter_target = user_info[user_id].get('twitter_target')
    if not twitter_target:
        update.message.reply_text('Twitter hedefi belirlenmedi. Lütfen hedefi girin.')
        return

    twitter_updates = get_twitter_updates(twitter_target)
    update.message.reply_text(f"Twitter hedefinden alınan güncellemeler:\n{twitter_updates}")

def forward_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info:
        update.message.reply_text('Lütfen önce kaynak ve hedef grup ID\'lerini ayarlayın.')
        return
    
    source_group_id = user_info[user_id].get('source_group')
    target_group_id = user_info[user_id].get('target_group')

    if update.message.chat_id == int(source_group_id):
        try:
            context.bot.forward_message(chat_id=target_group_id, 
                                        from_chat_id=update.message.chat_id, 
                                        message_id=update.message.message_id)
            update.message.reply_text(f"Mesaj {target_group_id} grubuna aktarıldı.")
        except TelegramError as e:
            update.message.reply_text(f"Mesaj aktarma hatası: {e}")
    else:
        update.message.reply_text('Bu grup, kaynak grup değil. Lütfen doğru gruptan mesaj gönderin.')
