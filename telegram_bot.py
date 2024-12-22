import json
from telegram import Update, Chat
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from twitter import get_twitter_updates
from config import TELEGRAM_BOT_TOKEN

# JSON dosyasını okuma ve yazma fonksiyonları
def load_user_data():
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open('user_data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Kullanıcı verisi JSON dosyasından yüklenir
user_info = load_user_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Merhaba! Ben Telegram Social Bot V2.\n'
        'Mesaj aktarımı yapmak için kaynak ve hedef grup bilgilerini girebilirsiniz.'
    )

async def set_source_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)  # ID string formatında olmalı
    source_group_id = update.message.text
    if user_id not in user_info:
        user_info[user_id] = {}

    user_info[user_id]['source_group'] = source_group_id
    save_user_data(user_info)  # Veriyi JSON dosyasına kaydet

    await update.message.reply_text(
        f"Kaynak grup {source_group_id} olarak ayarlandı.\nŞimdi hedef grup ID'sini girin."
    )

async def set_target_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id not in user_info or 'source_group' not in user_info[user_id]:
        await update.message.reply_text('Lütfen önce kaynak grup ID\'sini girin.')
        return

    target_group_id = update.message.text
    user_info[user_id]['target_group'] = target_group_id
    save_user_data(user_info)

    await update.message.reply_text(
        f"Hedef grup {target_group_id} olarak ayarlandı.\n"
        "Şimdi Twitter kullanıcı adı veya hashtag girin (örneğin: @username veya #hashtag)."
    )

async def set_twitter_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id not in user_info or 'source_group' not in user_info[user_id] or 'target_group' not in user_info[user_id]:
        await update.message.reply_text('Lütfen önce kaynak ve hedef grup ID\'lerini ayarlayın.')
        return

    twitter_target = update.message.text
    user_info[user_id]['twitter_target'] = twitter_target
    save_user_data(user_info)

    await update.message.reply_text(
        f"Twitter hedefi {twitter_target} olarak ayarlandı."
    )

async def forward_twitter_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    if user_id not in user_info or 'source_group' not in user_info[user_id] or 'target_group' not in user_info[user_id] or 'twitter_target' not in user_info[user_id]:
        await update.message.reply_text(
            'Lütfen önce kaynak, hedef grup ve Twitter hedefi bilgilerini ayarlayın.'
        )
        return

    twitter_target = user_info[user_id].get('twitter_target')
    twitter_updates = get_twitter_updates(twitter_target)  # Bu fonksiyonu uygun şekilde implement edin
    await update.message.reply_text(
        f"Twitter hedefinden alınan güncellemeler:\n{twitter_updates}"
    )
