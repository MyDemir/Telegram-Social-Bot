import os
import logging
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest
import tweepy
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Bot token'ları ve Twitter API anahtarlarını al
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TWITTER_API_KEY = os.getenv('API_KEY')
TWITTER_API_SECRET_KEY = os.getenv('API_SECRET_KEY')
TWITTER_ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

# Bot ve uygulama için log ayarları
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Twitter API ile bağlantı kuruyoruz
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

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

# Twitter kontrolü
async def start_twitter_check(context: ContextTypes.DEFAULT_TYPE):
    user_info = load_user_info()
    for twitter_username, data in user_info.items():
        tweets = api.user_timeline(screen_name=twitter_username, count=1, tweet_mode="extended")
        if tweets:
            tweet = tweets[0]
            last_tweet_id = data.get("last_tweet_id")
            if last_tweet_id != tweet.id:
                await send_tweet_notification(tweet, data["chat_id"])
                data["last_tweet_id"] = tweet.id
                save_user_info(user_info)

async def send_tweet_notification(tweet, chat_id):
    tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
    text = f"Yeni tweet! 🐦\n\n{tweet.full_text}\n\n🔗 [Tweeti Görüntüle]({tweet_url})"
    try:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", disable_web_page_preview=True)
    except BadRequest as e:
        logger.error(f"Mesaj gönderilirken hata oluştu: {e}")

async def get_channel_id(context, username):
    try:
        channel = await context.bot.get_chat(username)
        return channel.id
    except Exception as e:
        logger.error(f"Kanal ID'si alınırken hata oluştu: {e}")
        return None

async def is_user_admin(context, chat_id, user_id):
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
    except Exception as e:
        logger.error(f"Admin kontrolü yapılırken hata oluştu: {e}")
        return False

# Start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba! Bu bot, bir kanalda paylaşılan gönderileri diğer kanala bildirmek için tasarlandı. Kullanabileceğiniz komutlar:\n\n/set_channels @kaynakkanal @hedefkanal - Kaynak ve hedef kanalları ayarlayın.\n/add_twitter @kullaniciadi - Bir Twitter hesabı ekleyin.\nBaşlamak için /set_channels veya /add_twitter komutlarını kullanabilirsiniz.")

# Kanal ayarlama komutu
async def set_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_input = update.message.text.strip().split()
    
    if len(user_input) == 3 and user_input[0] == '/set_channels':
        source_channel_input = user_input[1]
        target_channel_input = user_input[2]
        
        source_channel_id = await get_channel_id(context, source_channel_input)
        target_channel_id = await get_channel_id(context, target_channel_input)

        if source_channel_id and target_channel_id:
            user_info = load_user_info()
            if user_id not in user_info:
                user_info[user_id] = {}
            user_info[user_id]["source_channel"] = source_channel_id
            user_info[user_id]["target_channel"] = target_channel_id
            save_user_info(user_info)
            await update.message.reply_text(f"Kanallar ayarlandı!\nKaynak: {source_channel_input} ({source_channel_id})\nHedef: {target_channel_input} ({target_channel_id})")
        else:
            await update.message.reply_text("Kanal bilgileri doğrulanamadı. Lütfen kullanıcı adını kontrol edin.")
    else:
        await update.message.reply_text("Lütfen iki kanal adı girin. Örnek: /set_channels @kaynakkanal @hedefkanal")

# Twitter kullanıcı adı ekleme komutu
async def add_twitter_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip().split()
    
    if len(user_input) == 2 and user_input[0] == '/add_twitter':
        twitter_username = user_input[1].lstrip('@')
        
        user_data = load_user_info()
        if twitter_username in user_data:
            await update.message.reply_text(f"{twitter_username} zaten takip ediliyor.")
        else:
            user_data[twitter_username] = {
                "last_tweet_id": None,
                "chat_id": update.message.chat.id,
                "twitter_username": twitter_username
            }
            save_user_info(user_data)
            await update.message.reply_text(f"{twitter_username} takip listesine eklendi.")
    else:
        await update.message.reply_text("Lütfen bir Twitter kullanıcı adı girin. Örnek: /add_twitter @elonmusk")

# Mesajları yönlendirmek yerine bilgilendirme mesajı gönder
async def forward_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    source_channel = None
    target_channel = None
    for info in load_user_info().values():
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

async def main() -> None:
    """Botu başlatma ve komut işleyicilerini ekleme"""
    global bot
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Komutlar ve işleyiciler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_channels", set_channels))
    application.add_handler(CommandHandler("add_twitter", add_twitter_user))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_content))

    # Job queue başlatma
    job_queue = application.job_queue
    job_queue.run_repeating(start_twitter_check, interval=60, first=0)

    # Uygulamayı çalıştır
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
