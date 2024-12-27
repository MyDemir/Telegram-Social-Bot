import tweepy
import os
import json
import time
from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# .env dosyasını yükle
load_dotenv()

# Twitter API anahtarlarını al
API_KEY = os.getenv("API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# Telegram bot token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

USER_INFO_FILE = "user_info.json"

# Tweepy API nesnesi
def create_api():
    try:
        auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        
        # API bağlantısı başarılı ise logla
        print("Twitter API'ye başarılı bir şekilde bağlanıldı.")
        return api
    except Exception as e:
        print(f"API bağlantısı başarısız: {e}")
    
# Kullanıcı bilgilerini yükle
def load_user_info():
    if os.path.exists(USER_INFO_FILE):
        with open(USER_INFO_FILE, "r") as f:
            return json.load(f)
    return {}

# Kullanıcı bilgilerini kaydet
def save_user_info(data):
    with open(USER_INFO_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Twitter kullanıcılarının tweet'lerini kontrol et
def check_tweets_periodically(interval=60):
    api = create_api()
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    user_data = load_user_info()

    while True:
        for username, info in user_data.items():
            try:
                tweets = api.user_timeline(screen_name=username, count=1, tweet_mode='extended')
                if tweets:
                    latest_tweet = tweets[0]
                    last_checked_tweet_id = info.get("last_tweet_id")

                    if last_checked_tweet_id is None or latest_tweet.id_str != last_checked_tweet_id:
                        user_data[username]["last_tweet_id"] = latest_tweet.id_str
                        save_user_info(user_data)

                        # Telegram kanalına gönder
                        send_telegram_notification(bot, info["chat_id"], username, latest_tweet)
            except tweepy.TweepError as e:
                print(f"{username} için hata oluştu: {e}")

        time.sleep(interval)

# Telegram kanalına tweet bildirimi gönder
def send_telegram_notification(bot, chat_id, username, tweet):
    tweet_text = tweet.full_text
    tweet_url = f"https://twitter.com/{username}/status/{tweet.id_str}"  # Tweetin URL'si

    # Yönlendirme butonu ekle
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Tweeti Görüntüle", url=tweet_url)]]
    )

    bot.send_message(
        chat_id=chat_id,
        text=f"🔔 @{username} yeni bir tweet attı:\n\n{tweet_text}",
        reply_markup=keyboard  # Yönlendirme butonu
    )
