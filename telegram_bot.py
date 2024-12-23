import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from twitter import get_twitter_updates  # Twitter güncellemelerini almak için ekledik

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
        "Kullanım: /set_channels @kaynakkanal @hedefkanal\n"
        "Twitter kullanıcı adı için: /set_twitter @kullaniciadi"
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
            save_user_info(user_info)
            await update.message.reply_text(
                f"Kanallar ayarlandı!\nKaynak: {source_channel_input} ({source_channel_id})\n"
                f"Hedef: {target_channel_input} ({target_channel_id})"
            )
        else:
            await update.message.reply_text("Kanal bilgileri doğrulanamadı. Lütfen kullanıcı adını kontrol edin.")
    else:
        await update.message.reply_text("Lütfen iki kanal adı girin. Örnek: /set_channels @kaynakkanal @hedefkanal")

# Twitter kullanıcı adı ayarlama komutu
async def set_twitter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if context.args:
        twitter_user = context.args[0]
        if user_id not in user_info:
            user_info[user_id] = {}
        user_info[user_id]["twitter_user"] = twitter_user
        save_user_info(user_info)
        await update.message.reply_text(f"Twitter kullanıcı adı {twitter_user} olarak ayarlandı!")
    else:
        await update.message.reply_text("Lütfen bir Twitter kullanıcı adı girin. Örnek: /set_twitter @kullaniciadi")

# Kanal ID'si alma
async def get_channel_id(context, username):
    try:
        channel = await context.bot.get_chat(username)
        return channel.id
    except Exception:
        return None

# Admin kontrolü
async def is_user_admin(context, chat_id, user_id):
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except Exception:
        return False

# Mesajları yönlendirmek yerine bilgilendirme mesajı gönder
async def forward_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return  # Mesaj yoksa çık

    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    source_channel = None
    target_channel = None
    for info in user_info.values():
        if info['source_channel'] == chat_id:
            source_channel = info['source_channel']
            target_channel = info['target_channel']
            break

    if source_channel is None or target_channel is None:
        return
    
    is_admin = await is_user_admin(context, source_channel, user_id)
    
    if not is_admin:
        return
    
    # Twitter güncellemelerini al
    twitter_user = user_info.get(user_id, {}).get("twitter_user")
    twitter_updates = ""
    if twitter_user:
        twitter_updates = await get_twitter_updates(twitter_user)  # get_twitter_updates fonksiyonu çağrılıyor

    source_channel_link = f"https://t.me/{update.message.chat.username}" if update.message.chat.username else "Kanalı Görüntüle"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Kanala Git", url=source_channel_link)]]
    )
    
    try:
        await context.bot.send_message(
            chat_id=target_channel,
            text=f"🔔 Yeni içerik var! Kaynak kanala göz atın! 🔔\n\n"
                 f"Twitter Güncellemeleri:\n{twitter_updates}",
            reply_markup=keyboard
        )
    except BadRequest as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")
