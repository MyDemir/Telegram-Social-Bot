import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from twitter import get_twitter_updates  # twitter.py'den fonksiyonu import ediyoruz.

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
        "Kullanım: /set_channels @kaynakkanal @hedefkanal\n\n"
        "Ayrıca X (Twitter) güncellemelerini almak için: /set_twitter @kullaniciadi"
    )

# Twitter güncellemelerini gönder
async def send_twitter_updates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info:
        await update.message.reply_text("Twitter kullanıcı adı ayarlanmadı. Lütfen önce /set_twitter komutunu kullanın.")
        return
    
    # Kullanıcıya ait Twitter kullanıcı adı alındı
    twitter_user = user_info[user_id].get("twitter_username")
    if not twitter_user:
        await update.message.reply_text("Twitter kullanıcı adı ayarlanmamış.")
        return
    
    # twitter.py dosyasındaki fonksiyonla Twitter'dan güncellemeleri alıyoruz
    twitter_updates = get_twitter_updates(twitter_user)  # Twitter'dan güncellemeleri al
    if twitter_updates:
        await update.message.reply_text(f"Twitter güncellemeleri:\n\n{twitter_updates}")
    else:
        await update.message.reply_text("Twitter'dan güncelleme alınamadı.")

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
    
    source_channel_link = f"https://t.me/{update.message.chat.username}" if update.message.chat.username else "Kanalı Görüntüle"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Kanala Git", url=source_channel_link)]]
    )
    
    try:
        await context.bot.send_message(
            chat_id=target_channel,
            text="🔔 Yeni içerik var! Kaynak kanala göz atın! 🔔",
            reply_markup=keyboard
        )
    except BadRequest as e:
        await update.message.reply_text(f"Bir hata oluştu: {e}")

# Twitter kullanıcı adı ayarlamak için fonksiyon
async def set_twitter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_input = update.message.text.strip().split()

    if len(user_input) == 2 and user_input[0] == '/set_twitter':
        twitter_username = user_input[1]

        # Kullanıcının Twitter adı kaydediliyor
        if user_id not in user_info:
            user_info[user_id] = {}
        
        user_info[user_id]["twitter_username"] = twitter_username
        save_user_info(user_info)

        await update.message.reply_text(f"Twitter kullanıcı adı ayarlandı: {twitter_username}")
    else:
        await update.message.reply_text("Lütfen geçerli bir Twitter kullanıcı adı girin. Örnek: /set_twitter @kullaniciadi")
