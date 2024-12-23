import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from twitter import get_twitter_updates  # twitter.py fonksiyonunu ekledim

# Logger kurulumu
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # DEBUG seviyesinde log tutacağız
)
logger = logging.getLogger(__name__)

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

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Merhaba! Bu bot, bir kanalda paylaşılan gönderileri diğer kanala bildirmek için tasarlandı.\n\n"
        "Kullanım:\n"
        "/set_channels @kaynakkanal @hedefkanal\n"
        "/set_twitter @TwitterKullaniciAdi"
    )

# Kanalları ayarlama
async def set_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_input = update.message.text.strip().split()

    if len(user_input) == 3:
        source_channel_input = user_input[1]
        target_channel_input = user_input[2]

        source_channel_id = await get_channel_id(context, source_channel_input)
        target_channel_id = await get_channel_id(context, target_channel_input)

        if source_channel_id and target_channel_id:
            if user_id not in user_info:
                user_info[user_id] = {}
                
            user_info[user_id].update({
                "source_channel": source_channel_id,
                "target_channel": target_channel_id
            })
            save_user_info(user_info)
            
            await update.message.reply_text(
                f"Kanallar ayarlandı!\nKaynak: {source_channel_input}\n"
                f"Hedef: {target_channel_input}"
            )
        else:
            await update.message.reply_text("Kanal bilgileri doğrulanamadı. Lütfen kullanıcı adını kontrol edin.")
    else:
        await update.message.reply_text("Kullanım: /set_channels @kaynakkanal @hedefkanal")

# Twitter kullanıcı adı ayarı
async def set_twitter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_input = update.message.text.strip().split()

    if len(user_input) == 2:
        twitter_username = user_input[1].lstrip('@')

        if user_id not in user_info:
            user_info[user_id] = {}

        user_info[user_id].update({
            "twitter_username": twitter_username
        })
        save_user_info(user_info)
        await update.message.reply_text(
            f"Twitter kullanıcı adı olarak @{twitter_username} ayarlandı!"
        )
    else:
        await update.message.reply_text("Kullanım: /set_twitter @kullaniciadi")

# Kaynak kanaldan hedef kanala sadece "Yeni gönderi var" bildirimi gönderme
async def send_channel_update_notification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    chat_id = update.message.chat.id
    user_id = update.message.from_user.id

    source_channel = None
    target_channel = None

    for info in user_info.values():
        if info.get('source_channel') == chat_id:
            source_channel = info['source_channel']
            target_channel = info['target_channel']
            break

    if not source_channel or not target_channel:
        return

    is_admin = await is_user_admin(context, source_channel, user_id)
    if not is_admin:
        return

    try:
        source_channel_link = f"https://t.me/{update.message.chat.username}" if update.message.chat.username else "Kaynak Kanalı"
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Kanala Git", url=source_channel_link)]]
        )
        await context.bot.send_message(
            chat_id=target_channel,
            text="🔔 Kaynak kanalda yeni bir gönderi var!",
            reply_markup=keyboard
        )
    except BadRequest as e:
        logger.error(f"Hata: {e}")
        await update.message.reply_text(f"Bir hata oluştu: {e}")

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

# Twitter güncellemelerini al
async def get_twitter_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_info or 'twitter_username' not in user_info[user_id]:
        await update.message.reply_text("Twitter kullanıcı adı ayarlanmamış.")
        return

    twitter_username = user_info[user_id]['twitter_username']
    tweet_text, tweet_url = get_twitter_updates(twitter_username)

    if tweet_text:
        await update.message.reply_text(f"Son Tweet: {tweet_text}\n{tweet_url}")
    else:
        # Eğer tweet alınamazsa hata mesajı
        await update.message.reply_text("Son tweet alınamadı. Lütfen daha sonra tekrar deneyin.")
