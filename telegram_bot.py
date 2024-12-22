import json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.error import BadRequest
from twitter import get_twitter_updates  # Twitter güncellemelerini almak için

# Kullanıcı bilgilerini saklayacak JSON dosyasını açma
def load_user_info():
    try:
        with open("user_info.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_info(user_info):
    with open("user_info.json", "w") as file:
        json.dump(user_info, file, indent=4)

user_info = load_user_info()

# Start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Merhaba! Bot, kaynak kanal ile hedef kanal arasında mesaj kopyalayacak.'
        ' İlk olarak, iki kanal ID\'si veya kullanıcı adı girmeniz gerekecek.'
    )

# Kanal ID'si veya kullanıcı adı al
async def set_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    # Admin kontrolü
    user_status = update.message.chat.get_member(user_id).status
    if user_status not in ["administrator", "creator"]:
        await update.message.reply_text('Bu kanalda admin değilsiniz. Admin olmalısınız.')
        return

    # Kanal ID'lerini al
    user_input = update.message.text.strip().split()
    
    if len(user_input) != 2:
        await update.message.reply_text('Lütfen iki kanal ID\'si veya kullanıcı adı girin.')
        return

    source_channel = user_input[0]
    target_channel = user_input[1]

    # Kanal bilgilerini kaydet
    user_info[user_id] = {"source_channel": source_channel, "target_channel": target_channel}
    save_user_info(user_info)

    await update.message.reply_text(
        f"Kaynak kanal: {source_channel}\nHedef kanal: {target_channel} olarak ayarlandı."
    )

    # Kullanıcıya kanal bilgilerini doğrulama mesajı gönder
    await update.message.reply_text(
        f"Kaydedilen bilgiler:\nKaynak Kanal: {source_channel}\nHedef Kanal: {target_channel}"
    )

# Mesajları kopyalamak için handler
async def forward_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    if user_id not in user_info:
        await update.message.reply_text('Lütfen önce kanal bilgilerini girin.')
        return

    source_channel = user_info[user_id]['source_channel']
    target_channel = user_info[user_id]['target_channel']
    
    # Mesajları hedef kanala ilet
    try:
        if update.message.chat.id == source_channel:
            await context.bot.send_message(target_channel, update.message.text)
            await update.message.reply_text(f"Mesaj başarıyla {target_channel} kanalına iletildi.")
    except BadRequest as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")

# Twitter güncellemelerini gönderme fonksiyonu
async def forward_twitter_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info:
        await update.message.reply_text('Lütfen önce kanal bilgilerini girin.')
        return

    twitter_target = user_info[user_id].get('twitter_target')
    if not twitter_target:
        await update.message.reply_text('Twitter hedefi belirlenmedi.')
        return

    twitter_updates = get_twitter_updates(twitter_target)
    await update.message.reply_text(
        f"Twitter hedefinden alınan güncellemeler:\n{twitter_updates}"
        )
