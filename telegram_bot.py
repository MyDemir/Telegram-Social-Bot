import json
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import BadRequest

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
        'Merhaba! Mesajları bir gruptan diğerine gönderebilirsiniz. Kanal bilgilerini ayarlamak için /set_channels komutunu kullanın.'
    )

# Kanal ayarlarını set etmek için
async def set_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_input = update.message.text.strip().split()

    if len(user_input) != 3:
        await update.message.reply_text(
            'Lütfen iki kanal ID\'si girin. Örnek: /set_channels @kaynakkanal @hedefkanal'
        )
        return

    # Kullanıcının source ve target kanallarını kaydet
    source_channel = user_input[1]
    target_channel = user_input[2]

    user_info[user_id] = {
        "source_channel": source_channel,
        "target_channel": target_channel
    }
    save_user_info(user_info)

    await update.message.reply_text(
        f"Kaynak kanal: {source_channel}\nHedef kanal: {target_channel} olarak ayarlandı."
    )

# Mesajları kopyalamak için handler
async def forward_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    
    # Kullanıcının ayarlarını alıyoruz
    if user_id not in user_info:
        await update.message.reply_text('Lütfen önce kanal bilgilerini ayarlayın.')
        return

    source_channel = user_info[user_id]['source_channel']
    target_channel = user_info[user_id]['target_channel']
    
    # Mesajları hedef kanala ilet
    try:
        if update.message.chat.id == source_channel:
            await context.bot.send_message(target_channel, update.message.text)
    except BadRequest as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")
