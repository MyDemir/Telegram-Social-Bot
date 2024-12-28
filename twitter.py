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
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
    # API bağlantı testi
    try:
        api.verify_credentials()
        print("✅ Twitter API bağlantısı başarılı!")
    except Exception as e:
        print(f"❌ Twitter API bağlantısı başarısız: {e}")
        exit()
    
    return api

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

    print("🚀 Bot başlatılıyor...")
    print(f"📂 Yüklenen kullanıcı verileri: {user_data}")
    
    while True:
        print("🔄 Döngü başladı...")
        for username, info in user_data.items():
            print(f"🟢 Kontrol edilen kullanıcı: @{username}")
            try:
                tweets = api.user_timeline(screen_name=username, count=1, tweet_mode='extended')
                print(f"🔍 @{username} için çekilen tweetler: {tweets}")
                
                if tweets:
                    latest_tweet = tweets[0]
                    last_checked_tweet_id = info.get("last_tweet_id")
                    
                    # Yeni tweet kontrolü
                    if last_checked_tweet_id is None or latest_tweet.id_str != last_checked_tweet_id:
                        print(f"📣 Yeni tweet bulundu: {latest_tweet.full_text}")
                        
                        user_data[username]["last_tweet_id"] = latest_tweet.id_str
                        save_user_info(user_data)
                        
                        # Telegram kanalına gönder
                        send_telegram_notification(bot, info["chat_id"], username, latest_tweet)
                    else:
                        print(f"🔕 Yeni tweet yok: {username}")
            except tweepy.TweepError as e:
                print(f"❌ {username} için hata oluştu: {e}")
            except Exception as e:
                print(f"⚠️ Beklenmeyen hata: {e}")

        time.sleep(interval)

# Telegram kanalına tweet bildirimi gönder
def send_telegram_notification(bot, chat_id, username, tweet):
    tweet_text = tweet.full_text
    tweet_url = f"https://twitter.com/{username}/status/{tweet.id_str}"  # Tweetin URL'si

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Tweeti Görüntüle", url=tweet_url)]]
    )

    bot.send_message(
        chat_id=chat_id,
        text=f"🔔 @{username} yeni bir tweet attı:\n\n{tweet_text}",
        reply_markup=keyboard
    )
    print(f"📤 Telegram'a gönderildi: {username} - {tweet_text}")

# Botu başlat
if __name__ == "__main__":
    check_tweets_periodically()
