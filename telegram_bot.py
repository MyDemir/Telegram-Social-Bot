import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
        "Merhaba! Bu bot, bir kanalda paylaşılan gönderileri diğer kanala bildirmek için tasarlandı.\n\n"
        "Kullanabileceğiniz komutlar:\n\n"
        "/set_channels @kaynakkanal @hedefkanal - Kaynak ve hedef kanalları ayarlayın.\n"
        "/add_twitter @kullaniciadi - Bir Twitter hesabı ekleyin."
    )

# Kanal ayarlama komutu
async def set_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_input = update.message.text.strip().split()

    if len(user_input) == 3 and user_input[0] == '/set_channels':
        source_channel_input = user_input[1]
        target_channel_input = user_input[2]

        source_channel_id = await get_channel_id(context, source_channel_input)
        target_channel_id = await get_channel_id(context, target_channel_input)

        if source_channel_id and target_channel_id:
            user_info[user_id] = {
                "source_channel": source_channel_id,
                "target_channel": target_channel_id
            }
            save_user_info(user_info)  # Veriyi kaydediyoruz
            await update.message.reply_text(
                f"Kanallar ayarlandı!\nKaynak: {source_channel_input}\nHedef: {target_channel_input}"
            )
        else:
            await update.message.reply_text("Kanal bilgileri doğrulanamadı.")
    else:
        await update.message.reply_text("Lütfen iki kanal adı girin. Örnek: /set_channels @kaynakkanal @hedefkanal")

# Twitter kullanıcı adı ekleme komutu
async def add_twitter_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.strip().split()

    if len(user_input) == 2 and user_input[0] == '/add_twitter':
        twitter_username = user_input[1].lstrip('@')
        
        user_data = load_user_info()

        if twitter_username in user_data:
            await update.message.reply_text(f"{twitter_username} zaten takip ediliyor.")
        else:
            user_data[twitter_username] = {
                "last_tweet_id": None,
                "chat_id": update.message.chat.id
            }
            save_user_info(user_data)  # Yeni veriyi kaydediyoruz
            await update.message.reply_text(f"{twitter_username} takip listesine eklendi.")
    else:
        await update.message.reply_text("Lütfen bir Twitter kullanıcı adı girin. Örnek: /add_twitter @elonmusk")

# Kanal ID'si alma
async def get_channel_id(context, username):
    try:
        channel = await context.bot.get_chat(username)
        return channel.id
    except Exception as e:
        return None

# Twitter'dan gelen tweetleri kontrol etme
async def start_twitter_check():
    user_data = load_user_info()
    for twitter_username, data in user_data.items():
        # Burada Twitter API kullanılarak tweet kontrolü yapılabilir
        # Örneğin: tweetler kontrol edilecek ve yeni tweet varsa bildirim yapılacak
        pass
