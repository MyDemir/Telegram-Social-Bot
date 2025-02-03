'''import tweepy
import os
import json
import time
import logging
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# .env dosyasını yükle
load_dotenv()

# Logger yapılandırma
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twitter API anahtarlarını al
API_KEY = os.getenv("API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

USER_INFO_FILE = "user_info.json"

def create_api():
    logger.info("Twitter API bağlantısı oluşturuluyor...")
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)  # wait_on_rate_limit_notify kaldırıldı
    logger.info("Twitter API bağlantısı başarılı.")
    return api

def load_user_info():
    try:
        with open(USER_INFO_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_info(data):
    logger.info(f"Kullanıcı verileri kaydediliyor: {data}")
    with open(USER_INFO_FILE, "w") as f:
        json.dump(data, f, indent=4)

def check_tweets_periodically(interval=60):
    api = create_api()
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    user_data = load_user_info()  # Kullanıcı verilerini alıyoruz

    while True:
        logger.info("Tweet kontrolü başlatıldı...")
        for username, info in user_data.items():
            try:
                logger.info(f"{username} kullanıcısının tweet'leri kontrol ediliyor...")
                tweets = api.user_timeline(screen_name=username, count=1, tweet_mode='extended')
                if tweets:
                    latest_tweet = tweets[0]
                    logger.info(f"{username} kullanıcısının son tweet'i: {latest_tweet.full_text}")
                    last_checked_tweet_id = info.get("last_tweet_id")

                    if last_checked_tweet_id is None or latest_tweet.id_str != last_checked_tweet_id:
                        user_data[username]["last_tweet_id"] = latest_tweet.id_str
                        save_user_info(user_data)  # Yeni tweet ID'si kaydediliyor
                        send_telegram_notification(bot, info["chat_id"], username, latest_tweet)
                    else:
                        logger.info(f"{username} için yeni tweet yok.")
            except tweepy.TweepError as e:
                logger.error(f"{username} için hata oluştu: {e}")

        logger.info(f"{interval} saniye uyku moduna geçiliyor...")
        time.sleep(interval)

def send_telegram_notification(bot, chat_id, username, tweet):
    tweet_text = tweet.full_text
    tweet_url = f"https://twitter.com/{username}/status/{tweet.id_str}"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Tweeti Görüntüle", url=tweet_url)]]
    )

    bot.send_message(
        chat_id=chat_id,
        text=f"🔔 @{username} yeni bir tweet attı:\n\n{tweet_text}",
        reply_markup=keyboard
    )
    logger.info(f"{username} kullanıcısının tweet'i Telegram'a gönderildi.")
    
if __name__ == "__main__":
    logger.info("Bot başlatılıyor...")
    check_tweets_periodically()
'''
import tweepy
import os
from dotenv import load_dotenv

# .env dosyasını yükleme
load_dotenv()

# Twitter API anahtarlarını yükleme
CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# Twitter API'ye bağlanma
def get_twitter_api():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    return api

# Twitter kullanıcısının son tweet'ini al
def get_last_tweet(twitter_username):
    api = get_twitter_api()
    try:
        tweets = api.user_timeline(screen_name=twitter_username, count=1, tweet_mode="extended")
        if tweets:
            return tweets[0].full_text
        else:
            return None
    except tweepy.TweepError as e:
        print(f"Hata: {e}")
        return None

# Son tweet'i hedef kanala gönderme
async def send_tweet_to_channel(update, context, twitter_username, target_channel):
    tweet = get_last_tweet(twitter_username)
    if tweet:
        try:
            await context.bot.send_message(
                chat_id=target_channel,
                text=f"Yeni tweet: {tweet}\n\n@{twitter_username} tarafından paylaşıldı.",
            )
        except Exception as e:
            await update.message.reply_text(f"Bir hata oluştu: {e}")
    else:
        await update.message.reply_text("Tweet alınamadı.")
